from collections.abc import Iterator
from dataclasses import dataclass
from math import isfinite

import av
from manim import *
from PIL import Image, ImageOps


@dataclass
class VideoStatus:
    time: float = 0
    container: av.container.InputContainer | None = None
    stream: av.video.stream.VideoStream | None = None
    frames: Iterator[av.VideoFrame] | None = None
    current_frame: av.VideoFrame | None = None
    next_frame: av.VideoFrame | None = None
    exhausted: bool = False
    closed: bool = False

    def __deepcopy__(self, memo):
        # Keep copied mobjects attached to the same decoder and playback clock
        return self


class VideoMobject(ImageMobject):
    """Play a video while preserving its alpha channel.

    Parameters
    ----------
    filename
        Path to the source video
    imageops
        Optional PIL image operation applied to each RGBA frame
        Operations that convert to RGB will discard transparency
    speed
        Nonnegative playback multiplier, with 0 pausing playback
    loop
        Repeat the selected interval from start_time
    start_time
        Start position in source video seconds, defaults to 0
    end_time
        Exclusive end position in source video seconds
        None uses the natural video end
        Non-looping playback holds the last displayed frame before the end
    close_at_end
        Close the decoder after non-looping playback finishes
        Defaults to True and leaves the final image visible
        Looping playback keeps the decoder open

    Notes
    -----
    remaining_time() returns seconds until the current pass ends
    close() releases the decoder and stops this object's updater
    Copies share playback state and the decoder

    Adapted from the original OpenCV VideoMobject by
    Uwe Zimmermann and Abulafia
    """

    def __init__(
        self,
        filename=None,
        imageops=None,
        speed=1.0,
        loop=False,
        start_time=0.0,
        end_time=None,
        close_at_end: bool = True,
        **kwargs,
    ):
        # Validate the interval and forward playback speed
        if not isfinite(start_time) or start_time < 0:
            raise ValueError("start_time must be finite and nonnegative")
        if end_time is not None and (
            not isfinite(end_time) or end_time <= start_time
        ):
            raise ValueError("end_time must be finite and greater than start_time")
        if not isfinite(speed) or speed < 0:
            raise ValueError("speed must be finite and nonnegative")

        self.filename = filename
        self.imageops = imageops
        self.speed = speed
        self.loop = loop
        self.close_at_end = close_at_end
        self.start_ms = start_time * 1000
        self.end_ms = None if end_time is None else end_time * 1000
        self.status = VideoStatus(time=self.start_ms)

        # Open the decoder and release it if initialization fails
        container = av.open(filename)
        self.status.container = container
        try:
            if not container.streams.video:
                raise ValueError("The file contains no video stream")

            stream = container.streams.video[0]
            self.status.stream = stream
            self._stream_start = stream.start_time or 0

            # Prefer video duration over the duration of other container streams
            self.duration_ms = None
            if stream.duration is not None:
                self.duration_ms = float(
                    stream.duration * stream.time_base
                ) * 1000
            elif container.duration is not None:
                self.duration_ms = container.duration / av.time_base * 1000

            # Stop at the natural video end if it precedes the requested end
            self._playback_end_ms = self.end_ms
            if self.duration_ms is not None:
                if self._playback_end_ms is None:
                    self._playback_end_ms = self.duration_ms
                else:
                    self._playback_end_ms = min(
                        self._playback_end_ms, self.duration_ms
                    )
                if self.start_ms >= self._playback_end_ms:
                    raise ValueError("start_time is beyond the video end")

            # Decode the initial image at the selected start
            frame = self._read_frame(self.start_ms, seek=True)
            if frame is None:
                raise ValueError("No video frame is available at start_time")

            super().__init__(self._frame_image(frame), **kwargs)
        except Exception:
            container.close()
            self.status.closed = True
            raise

        # Advance playback whenever Manim updates this mobject
        self.add_updater(self.video_updater)

    def _frame_time_ms(self, frame):
        # Normalize source timestamps so playback starts at video time zero
        if frame.pts is None:
            raise ValueError("The video frame has no presentation timestamp")
        start_seconds = float(
            self._stream_start * self.status.stream.time_base
        )
        return (float(frame.pts * frame.time_base) - start_seconds) * 1000

    def _next_frame(self):
        # Mark the natural end when the decoder runs out of frames
        frame = next(self.status.frames, None)
        if frame is None:
            self.status.exhausted = True
        return frame

    def _read_frame(self, time_ms, *, seek=False):
        status = self.status
        stream = status.stream

        # Seek to a preceding keyframe when starting or wrapping playback
        if seek:
            timestamp = self._stream_start + int(
                time_ms / 1000 / stream.time_base
            )
            status.container.seek(
                timestamp, stream=stream, backward=True
            )
            status.frames = iter(status.container.decode(stream))
            status.current_frame = None
            status.next_frame = None
            status.exhausted = False

        # Keep one frame ahead so the current image covers the requested time
        if status.next_frame is None and not status.exhausted:
            status.next_frame = self._next_frame()

        while (
            status.next_frame is not None
            and self._frame_time_ms(status.next_frame) <= time_ms
        ):
            status.current_frame = status.next_frame
            status.next_frame = self._next_frame()

        return status.current_frame

    def _frame_image(self, frame):
        # Preserve the decoded alpha channel all the way into the PIL image
        img = Image.fromarray(frame.to_ndarray(format="rgba"))
        if self.imageops is not None:
            img = self.imageops(img)
        return img

    def remaining_time(self) -> float:
        """Return playback seconds until the end of the current pass."""
        # Use the selected boundary or the natural video duration
        end_ms = self._playback_end_ms
        if end_ms is None:
            raise ValueError("Cannot determine the video's duration")

        # Completed playback has no remaining time, even when speed is zero
        remaining_ms = max(0.0, end_ms - self.status.time)
        if remaining_ms == 0:
            return 0.0

        # A stationary playback clock has no finite finish time
        if self.speed == 0:
            return float("inf")
        if self.speed < 0:
            raise ValueError("remaining_time requires nonnegative speed")

        return remaining_ms / (1000 * self.speed)

    def video_updater(self, mobj, dt):
        # Skip paused or closed playback without decoding another frame
        status = mobj.status
        if dt <= 0 or mobj.speed == 0 or status.closed:
            return
        if not isfinite(mobj.speed) or mobj.speed < 0:
            raise ValueError("speed must be finite and nonnegative")

        next_time = status.time + 1000 * dt * mobj.speed
        end_ms = mobj._playback_end_ms
        seek = False
        finished = False

        # Wrap overshoot into the interval or select its final frame
        if end_ms is not None and next_time >= end_ms:
            if mobj.loop:
                duration = end_ms - mobj.start_ms
                next_time = (
                    mobj.start_ms
                    + (next_time - mobj.start_ms) % duration
                )
                seek = True
            else:
                next_time = end_ms
                finished = True

        # Keep the end exclusive while still decoding the final interval frame
        sample_time = (
            np.nextafter(end_ms, -np.inf) if finished else next_time
        )
        previous_frame = status.current_frame
        frame = mobj._read_frame(sample_time, seek=seek)
        status.time = next_time

        # Infer the natural end after decoding if duration metadata was missing
        if end_ms is None and status.exhausted and frame is not None:
            frame_duration = float(frame.duration * frame.time_base) * 1000
            if frame_duration <= 0:
                rate = status.stream.average_rate
                if not rate:
                    raise ValueError("Cannot determine the final frame duration")
                frame_duration = 1000 / float(rate)

            mobj._playback_end_ms = (
                mobj._frame_time_ms(frame) + frame_duration
            )

            # Apply the newly discovered end on the next update
            status.time = min(status.time, mobj._playback_end_ms)

        # Convert pixels only when playback selects a different decoded frame
        if frame is not None and frame is not previous_frame:
            img = mobj._frame_image(frame)
            mobj.pixel_array = change_to_rgba_array(
                np.asarray(img), mobj.pixel_array_dtype
            )

        # Release the decoder after presenting the final frame
        if finished and mobj.close_at_end:
            mobj.close()

    def seek(self, time: float) -> None:
        """Display an absolute source time in seconds, preserving pause state."""
        # Keep the requested position within the selected playback interval
        target_ms = time * 1000
        if not isfinite(time) or target_ms < self.start_ms:
            raise ValueError("Seek time must be finite and at or after start_time")
        if self._playback_end_ms is not None and target_ms >= self._playback_end_ms:
            raise ValueError("Seek time must be before the playback end")

        # Reopen a finished video while retaining its previous pause state
        was_paused = self.updating_suspended
        if self.status.closed:
            self.restart()
            if was_paused:
                self.suspend_updating()

        # Decode the requested frame without advancing scene time
        frame = self._read_frame(target_ms, seek=True)
        if frame is None:
            raise ValueError("No video frame is available at the requested time")

        # Replace the image while preserving geometry and attached children
        img = self._frame_image(frame)
        self.pixel_array = change_to_rgba_array(
            np.asarray(img), self.pixel_array_dtype
        )
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        self.status.time = target_ms

    def restart(self) -> None:
        """Reopen the source and resume playback from the selected start."""
        # Prepare a fresh decoder and the selected interval's initial frame
        fresh = VideoMobject(
            filename=self.filename,
            imageops=self.imageops,
            speed=self.speed,
            loop=self.loop,
            start_time=self.start_ms / 1000,
            end_time=None if self.end_ms is None else self.end_ms / 1000,
            close_at_end=self.close_at_end,
        )

        # Close the previous decoder before adopting the reopened playback state
        self.close()
        self.status = fresh.status
        self._stream_start = fresh._stream_start
        self.duration_ms = fresh.duration_ms
        self._playback_end_ms = fresh._playback_end_ms

        # Replace the frame without changing this object's displayed geometry
        self.pixel_array = fresh.pixel_array.copy()
        self.orig_alpha_pixel_array = fresh.orig_alpha_pixel_array.copy()

        # Attach this object's updater and resume playback
        self.add_updater(self.video_updater)
        self.resume_updating()

    def close(self):
        """Stop updating this object and close its shared video decoder."""
        # Release the container once, including when copies share this status
        self.remove_updater(self.video_updater)
        if not self.status.closed:
            self.status.container.close()
            self.status.closed = True


class UsageExample(Scene):
    def construct(self):
        video1 = (
            VideoMobject(
                filename=("video1.mp4"),
                speed=1.0,
            )
            .scale_to_fit_width(5)
            .to_corner(UL)
        )
        video2 = (
            VideoMobject(
                filename=("video2.mkv"),
                speed=3.0,
                loop=True,
                imageops=ImageOps.mirror,
            )
            .scale_to_fit_width(5)
            .to_corner(UR)
        )
        v1 = Group(video1, SurroundingRectangle(video1))
        v2 = Group(video2, SurroundingRectangle(video2))
        self.add(v1, v2)
        self.wait(2)
        self.play(v2.animate.shift(3 * DL), run_time=6)
        self.next_slide()

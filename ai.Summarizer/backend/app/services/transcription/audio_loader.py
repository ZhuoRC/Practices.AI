"""
Audio and video file loader service.
Handles audio extraction from video files and audio format conversion.
"""
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional
from pydub import AudioSegment

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    # Fallback for newer moviepy versions
    try:
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None

logger = logging.getLogger(__name__)


class AudioVideoLoader:
    """Service for loading and processing audio/video files."""

    # Supported formats
    AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma'}
    VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}

    @staticmethod
    def _safe_delete_temp_file(temp_path: Optional[Path], max_retries: int = 3, delay: float = 0.5):
        """
        Safely delete a temporary file with retry logic for Windows file locking.

        Args:
            temp_path: Path to temporary file (can be None)
            max_retries: Maximum number of deletion attempts
            delay: Delay between retries in seconds
        """
        if temp_path is None or not temp_path.exists():
            return

        for attempt in range(max_retries):
            try:
                temp_path.unlink()
                logger.debug(f"Temp file deleted: {temp_path}")
                return
            except PermissionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to delete temp file (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to delete temp file after {max_retries} attempts: {temp_path}")
            except Exception as e:
                logger.warning(f"Error deleting temp file: {e}")
                return

    @staticmethod
    def is_audio_file(filename: str) -> bool:
        """Check if filename is a supported audio format."""
        ext = Path(filename).suffix.lower()
        return ext in AudioVideoLoader.AUDIO_FORMATS

    @staticmethod
    def is_video_file(filename: str) -> bool:
        """Check if filename is a supported video format."""
        ext = Path(filename).suffix.lower()
        return ext in AudioVideoLoader.VIDEO_FORMATS

    @staticmethod
    def extract_audio_from_video(video_bytes: bytes, file_extension: str) -> bytes:
        """
        Extract audio track from video file.

        Args:
            video_bytes: Raw video file bytes
            file_extension: Original file extension (e.g., '.mp4')

        Returns:
            Audio data as WAV bytes

        Raises:
            Exception: If audio extraction fails
        """
        if VideoFileClip is None:
            raise Exception("moviepy is not properly installed. Please reinstall: pip install moviepy")

        temp_video_path = None
        temp_audio_path = None

        try:
            # Create temporary video file
            with tempfile.NamedTemporaryFile(
                suffix=file_extension,
                delete=False
            ) as temp_video:
                temp_video_path = Path(temp_video.name)
                temp_video.write(video_bytes)

            logger.info(f"Extracting audio from video: {file_extension}")

            # Load video and extract audio
            video_clip = VideoFileClip(str(temp_video_path))

            if video_clip.audio is None:
                raise Exception("Video file contains no audio track")

            # Create temporary audio file (WAV format)
            temp_audio_path = temp_video_path.with_suffix('.wav')
            video_clip.audio.write_audiofile(
                str(temp_audio_path),
                codec='pcm_s16le',
                verbose=False,
                logger=None
            )

            # Close video clip to release resources
            video_clip.close()

            # Read audio bytes
            with open(temp_audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            logger.info(f"Audio extracted successfully: {len(audio_bytes)} bytes")

            return audio_bytes

        except Exception as e:
            logger.error(f"Failed to extract audio from video: {str(e)}")
            raise Exception(f"Audio extraction failed: {str(e)}")

        finally:
            # Clean up temporary files (with retry logic for Windows)
            AudioVideoLoader._safe_delete_temp_file(temp_video_path)
            AudioVideoLoader._safe_delete_temp_file(temp_audio_path)

    @staticmethod
    def convert_audio_to_format(audio_bytes: bytes, file_extension: str, target_format: str) -> bytes:
        """
        Convert audio file to specified format.

        Args:
            audio_bytes: Raw audio file bytes
            file_extension: Original file extension (e.g., '.mp3', '.m4a')
            target_format: Target format (without dot, e.g., 'wav', 'mp3')

        Returns:
            Audio data in target format

        Raises:
            Exception: If conversion fails
        """
        temp_input_path = None
        temp_output_path = None

        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(
                suffix=file_extension,
                delete=False
            ) as temp_input:
                temp_input_path = Path(temp_input.name)
                temp_input.write(audio_bytes)

            logger.info(f"Converting audio format: {file_extension} -> {target_format}")

            # Load audio file using pydub
            format_name = file_extension[1:] if file_extension.startswith('.') else file_extension
            audio = AudioSegment.from_file(str(temp_input_path), format=format_name)

            # Export as target format
            temp_output_path = temp_input_path.with_suffix(f'.{target_format}')
            audio.export(str(temp_output_path), format=target_format)

            # Read output bytes
            with open(temp_output_path, 'rb') as output_file:
                output_bytes = output_file.read()

            logger.info(f"Audio converted successfully: {len(output_bytes)} bytes")

            return output_bytes

        except Exception as e:
            logger.error(f"Failed to convert audio format: {str(e)}")
            raise Exception(f"Audio conversion failed: {str(e)}")

        finally:
            # Clean up temporary files (with retry logic for Windows)
            AudioVideoLoader._safe_delete_temp_file(temp_input_path)
            AudioVideoLoader._safe_delete_temp_file(temp_output_path)

    @staticmethod
    def convert_audio_to_wav(audio_bytes: bytes, file_extension: str) -> bytes:
        """
        Convert audio file to WAV format for consistent processing.

        Args:
            audio_bytes: Raw audio file bytes
            file_extension: Original file extension (e.g., '.mp3', '.m4a')

        Returns:
            Audio data as WAV bytes

        Raises:
            Exception: If conversion fails
        """
        temp_input_path = None
        temp_output_path = None

        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(
                suffix=file_extension,
                delete=False
            ) as temp_input:
                temp_input_path = Path(temp_input.name)
                temp_input.write(audio_bytes)

            logger.info(f"Converting audio format: {file_extension} -> WAV")

            # Load audio file using pydub
            # Automatically detects format based on file extension
            format_name = file_extension[1:]  # Remove leading dot
            audio = AudioSegment.from_file(str(temp_input_path), format=format_name)

            # Export as WAV
            temp_output_path = temp_input_path.with_suffix('.wav')
            audio.export(str(temp_output_path), format='wav')

            # Read WAV bytes
            with open(temp_output_path, 'rb') as wav_file:
                wav_bytes = wav_file.read()

            logger.info(f"Audio converted successfully: {len(wav_bytes)} bytes")

            return wav_bytes

        except Exception as e:
            logger.error(f"Failed to convert audio format: {str(e)}")
            raise Exception(f"Audio conversion failed: {str(e)}")

        finally:
            # Clean up temporary files (with retry logic for Windows)
            AudioVideoLoader._safe_delete_temp_file(temp_input_path)
            AudioVideoLoader._safe_delete_temp_file(temp_output_path)

    @classmethod
    def prepare_audio_for_transcription(
        cls,
        file_bytes: bytes,
        filename: str
    ) -> tuple[bytes, str]:
        """
        Prepare audio/video file for transcription.

        Video files: Always extract audio to WAV format
        Audio files: Use native format if supported, otherwise convert to WAV

        Args:
            file_bytes: Raw file bytes
            filename: Original filename

        Returns:
            Tuple of (audio_bytes, file_extension)

        Raises:
            Exception: If file processing fails
        """
        file_extension = Path(filename).suffix.lower()

        # Audio formats natively supported by transcription services
        AUDIO_NATIVE_FORMATS = {'.mp3', '.wav', '.m4a', '.mpeg', '.mpga'}

        # Handle video files - always extract audio to WAV
        if cls.is_video_file(filename):
            logger.info(f"Processing video file: {filename} - extracting audio to WAV")
            # Always extract audio from video files to WAV format
            # Video containers (mp4, avi, etc.) cannot be sent to transcription APIs
            audio_bytes = cls.extract_audio_from_video(file_bytes, file_extension)
            return audio_bytes, '.wav'

        # Handle audio files
        elif cls.is_audio_file(filename):
            logger.info(f"Processing audio file: {filename}")

            # If format is natively supported, use it directly
            if file_extension in AUDIO_NATIVE_FORMATS:
                logger.info(f"Audio format {file_extension} is natively supported, using directly")
                return file_bytes, file_extension

            # For other formats, convert to WAV
            try:
                audio_bytes = cls.convert_audio_to_wav(file_bytes, file_extension)
                return audio_bytes, '.wav'
            except Exception as e:
                logger.warning(f"Conversion failed, attempting to use original format: {e}")
                # If conversion fails, try using the original format anyway
                return file_bytes, file_extension

        else:
            raise Exception(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: {cls.AUDIO_FORMATS | cls.VIDEO_FORMATS}"
            )

    @staticmethod
    def get_audio_duration(audio_bytes: bytes, file_extension: str = '.wav') -> float:
        """
        Get duration of audio file in seconds.

        Note: This function requires ffmpeg to be installed. If ffmpeg is not available,
        it will return 0.0 (duration will be determined during transcription instead).

        Args:
            audio_bytes: Raw audio file bytes
            file_extension: Audio file extension

        Returns:
            Duration in seconds, or 0.0 if duration cannot be determined
        """
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=file_extension,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(audio_bytes)

            format_name = file_extension[1:]
            audio = AudioSegment.from_file(str(temp_path), format=format_name)
            duration = len(audio) / 1000.0  # Convert milliseconds to seconds

            logger.info(f"Audio duration: {duration:.2f} seconds")
            return duration

        except FileNotFoundError as e:
            # ffmpeg not found - this is OK, duration will be determined during transcription
            logger.info("ffmpeg not available, skipping duration calculation (will be determined during transcription)")
            return 0.0
        except Exception as e:
            logger.warning(f"Failed to get audio duration: {str(e)}")
            return 0.0
        finally:
            # Clean up temporary file (with retry logic for Windows)
            AudioVideoLoader._safe_delete_temp_file(temp_path)

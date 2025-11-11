#!/usr/bin/env python3
"""
XTTS-v2 Installation Test Script

This script tests the XTTS-v2 installation and functionality.
It performs various checks to ensure the TTS service is working correctly.
"""

import os
import sys
import time
import asyncio
import tempfile
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XTTSV2Tester:
    """Test suite for XTTS-v2 installation."""
    
    def __init__(self):
        self.test_results = []
        self.temp_files = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✓ PASS" if success else "✗ FAIL"
        self.test_results.append((test_name, success, message))
        logger.info(f"{status}: {test_name}")
        if message:
            logger.info(f"    {message}")
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except OSError as e:
                logger.warning(f"Failed to cleanup {temp_file}: {e}")
    
    def test_python_imports(self):
        """Test if all required packages can be imported."""
        try:
            import torch
            self.log_test("PyTorch import", True, f"Version: {torch.__version__}")
        except ImportError as e:
            self.log_test("PyTorch import", False, str(e))
            return False
        
        try:
            import torchaudio
            self.log_test("TorchAudio import", True, f"Version: {torchaudio.__version__}")
        except ImportError as e:
            self.log_test("TorchAudio import", False, str(e))
            return False
        
        try:
            import librosa
            self.log_test("Librosa import", True, f"Version: {librosa.__version__}")
        except ImportError as e:
            self.log_test("Librosa import", False, str(e))
        
        try:
            import soundfile
            self.log_test("SoundFile import", True, f"Version: {soundfile.__version__}")
        except ImportError as e:
            self.log_test("SoundFile import", False, str(e))
        
        try:
            import TTS
            self.log_test("TTS library import", True, f"Version: {TTS.__version__}")
        except ImportError as e:
            self.log_test("TTS library import", False, str(e))
            return False
        
        return True
    
    def test_gpu_availability(self):
        """Test GPU availability and CUDA support."""
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                self.log_test("GPU availability", True, f"Found {gpu_count} GPU(s): {gpu_name}")
                return True
            else:
                self.log_test("GPU availability", False, "CUDA not available, will use CPU")
                return False
        except Exception as e:
            self.log_test("GPU availability", False, str(e))
            return False
    
    def test_model_loading(self):
        """Test XTTS-v2 model loading."""
        try:
            import torch
            from TTS.api import TTS
            
            logger.info("Loading XTTS-v2 model (this may take 10-30 minutes on first run)...")
            start_time = time.time()
            
            # Fix for PyTorch 2.6+ safety features
            try:
                # Add safe globals for TTS config
                torch.serialization.add_safe_globals([
                    'TTS.tts.configs.xtts_config.XttsConfig'
                ])
                logger.info("Added TTS config to safe globals")
            except AttributeError:
                # Older PyTorch version, no need to add safe globals
                logger.info("PyTorch version doesn't require safe globals configuration")
            
            # Try to load model
            tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)
            
            load_time = time.time() - start_time
            self.log_test("XTTS-v2 model loading", True, f"Loaded in {load_time:.1f} seconds")
            
            # Check available speakers (XTTS-v2 may not have speakers attribute)
            try:
                speakers = getattr(tts, 'speakers', None)
                if speakers:
                    self.log_test("Model speakers", True, f"Found {len(speakers)} speakers")
                else:
                    self.log_test("Model speakers", True, "XTTS-v2 loaded successfully (no speakers list)")
            except Exception as e:
                self.log_test("Model speakers", False, str(e))
            
            return tts
            
        except Exception as e:
            self.log_test("XTTS-v2 model loading", False, str(e))
            return None
    
    def test_basic_synthesis(self, tts_instance):
        """Test basic text-to-speech synthesis."""
        if not tts_instance:
            self.log_test("Basic synthesis", False, "No TTS instance available")
            return False
        
        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name
                self.temp_files.append(output_path)
            
            # Test basic synthesis
            test_text = "Hello, this is a test of the XTTS-v2 text-to-speech system."
            start_time = time.time()
            
            # For XTTS-v2, we need to provide a speaker_wav file
            # Use the default voice sample
            voice_samples_path = Path("voice_samples")
            default_sample = voice_samples_path / "default.wav"
            
            if default_sample.exists():
                tts_instance.tts_to_file(
                    text=test_text,
                    speaker_wav=str(default_sample),
                    language="en",
                    file_path=output_path
                )
            else:
                self.log_test("Basic synthesis", False, "No default voice sample found")
                return False
            
            synthesis_time = time.time() - start_time
            
            # Check if file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path)
                self.log_test("Basic synthesis", True, 
                            f"Generated {file_size} bytes in {synthesis_time:.2f} seconds")
                return True
            else:
                self.log_test("Basic synthesis", False, "No output file generated")
                return False
                
        except Exception as e:
            self.log_test("Basic synthesis", False, str(e))
            return False
    
    def test_multilingual_synthesis(self, tts_instance):
        """Test multilingual synthesis capabilities."""
        if not tts_instance:
            self.log_test("Multilingual synthesis", False, "No TTS instance available")
            return False
        
        try:
            # Test different languages
            test_cases = [
                ("es", "Hola, esto es una prueba en español."),
                ("fr", "Bonjour, ceci est un test en français."),
                ("de", "Hallo, dies ist ein Test auf Deutsch."),
                ("zh", "你好，这是一个中文测试。")
            ]
            
            success_count = 0
            for lang_code, text in test_cases:
                try:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        output_path = temp_file.name
                        self.temp_files.append(output_path)
                    
                    # For XTTS-v2, we need to provide a speaker_wav file
                    voice_samples_path = Path("voice_samples")
                    default_sample = voice_samples_path / "default.wav"
                    
                    if default_sample.exists():
                        tts_instance.tts_to_file(
                            text=text,
                            speaker_wav=str(default_sample),
                            language=lang_code,
                            file_path=output_path
                        )
                    else:
                        self.log_test(f"Multilingual synthesis ({lang_code})", False, "No default voice sample found")
                        continue
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        success_count += 1
                        self.log_test(f"Multilingual synthesis ({lang_code})", True)
                    else:
                        self.log_test(f"Multilingual synthesis ({lang_code})", False)
                        
                except Exception as e:
                    self.log_test(f"Multilingual synthesis ({lang_code})", False, str(e))
            
            self.log_test("Multilingual synthesis overall", 
                        success_count == len(test_cases), 
                        f"Success: {success_count}/{len(test_cases)} languages")
            return success_count > 0
            
        except Exception as e:
            self.log_test("Multilingual synthesis", False, str(e))
            return False
    
    def test_voice_cloning(self, tts_instance):
        """Test voice cloning functionality."""
        if not tts_instance:
            self.log_test("Voice cloning", False, "No TTS instance available")
            return False
        
        # Check if voice samples directory exists and has files
        voice_samples_dir = Path("voice_samples")
        if not voice_samples_dir.exists():
            self.log_test("Voice cloning", False, "No voice_samples directory found")
            return False
        
        # Look for voice sample files
        sample_files = list(voice_samples_dir.glob("*.wav")) + list(voice_samples_dir.glob("*.mp3"))
        
        if not sample_files:
            self.log_test("Voice cloning", False, "No voice sample files found in voice_samples/")
            logger.info("  To test voice cloning, add audio files to voice_samples/ directory")
            return False
        
        try:
            # Test with the first available sample
            sample_file = sample_files[0]
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name
                self.temp_files.append(output_path)
            
            test_text = "This is a test of voice cloning using my own voice sample."
            
            tts_instance.tts_to_file(
                text=test_text,
                speaker_wav=str(sample_file),
                language="en",
                file_path=output_path
            )
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.log_test("Voice cloning", True, f"Used sample: {sample_file.name}")
                return True
            else:
                self.log_test("Voice cloning", False, "No output file generated")
                return False
                
        except Exception as e:
            self.log_test("Voice cloning", False, str(e))
            return False
    
    async def test_api_integration(self):
        """Test integration with the TTS API service."""
        try:
            # Try to import and test the XTTS-v2 service
            from tts_services.xtts_v2_tts import XTTSV2TTSService
            from tts_services.base import TTSRequest, AudioFormat
            
            # Create service instance with test configuration
            config = {
                "XTTS_V2_DEFAULT_SPEAKER": "default",
                "XTTS_V2_DEFAULT_LANGUAGE": "en",
                "XTTS_V2_USE_GPU": False
            }
            
            service = XTTSV2TTSService(config)
            
            # Test health check
            health_ok = await service.health_check()
            self.log_test("API health check", health_ok)
            
            if not health_ok:
                return False
            
            # Test getting available voices
            voices = await service.get_available_voices()
            self.log_test("Get available voices", True, f"Found {len(voices)} voices")
            
            # Test synthesis through API
            request = TTSRequest(
                text="Hello from the XTTS-v2 API!",
                voice_id="default_female",
                output_format=AudioFormat.WAV
            )
            
            response = await service.synthesize(request)
            
            if response.audio_data and len(response.audio_data) > 0:
                self.log_test("API synthesis", True, 
                            f"Generated {len(response.audio_data)} bytes")
                return True
            else:
                self.log_test("API synthesis", False, "No audio data received")
                return False
                
        except Exception as e:
            self.log_test("API integration", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests and generate report."""
        logger.info("Starting XTTS-v2 Installation Test Suite")
        logger.info("=" * 50)
        
        # Basic import tests
        logger.info("\n1. Testing Package Imports...")
        imports_ok = self.test_python_imports()
        
        if not imports_ok:
            logger.error("Critical imports failed. Cannot continue testing.")
            return False
        
        # GPU availability test
        logger.info("\n2. Testing GPU Availability...")
        gpu_available = self.test_gpu_availability()
        
        # Model loading test
        logger.info("\n3. Testing Model Loading...")
        tts_instance = self.test_model_loading()
        
        if not tts_instance:
            logger.error("Model loading failed. Cannot continue functionality tests.")
            return False
        
        # Synthesis tests
        logger.info("\n4. Testing Basic Synthesis...")
        basic_ok = self.test_basic_synthesis(tts_instance)
        
        logger.info("\n5. Testing Multilingual Synthesis...")
        multilingual_ok = self.test_multilingual_synthesis(tts_instance)
        
        logger.info("\n6. Testing Voice Cloning...")
        voice_cloning_ok = self.test_voice_cloning(tts_instance)
        
        logger.info("\n7. Testing API Integration...")
        api_ok = await self.test_api_integration()
        
        # Generate summary
        logger.info("\n" + "=" * 50)
        logger.info("TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, message in self.test_results:
            status = "✓ PASS" if success else "✗ FAIL"
            logger.info(f"{status}: {test_name}")
            if message:
                logger.info(f"    {message}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! XTTS-v2 is ready to use.")
        elif passed >= total * 0.8:
            logger.info("✅ Most tests passed. XTTS-v2 should work correctly.")
        else:
            logger.warning("⚠️  Multiple tests failed. Check the installation.")
        
        # Provide recommendations
        logger.info("\nRECOMMENDATIONS:")
        if not gpu_available:
            logger.info("- Consider installing CUDA for GPU acceleration")
        if not voice_cloning_ok:
            logger.info("- Add voice samples to voice_samples/ directory for voice cloning")
        if not api_ok:
            logger.info("- Check the API service configuration")
        
        return passed >= total * 0.8


async def main():
    """Main test function."""
    tester = XTTSV2Tester()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during testing: {e}")
        return 1
    finally:
        tester.cleanup()


if __name__ == "__main__":
    # Run the test suite
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

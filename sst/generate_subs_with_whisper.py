def _generate_subs_with_whisper(self, generated_srt_path):
        """Generates subtitles using Whisper. This is the final fallback."""
        print(f"\n--- Generating Subtitles with Whisper ---", flush=True)

        # Create a predictable scratch directory for intermediate files
        scratch_dir = os.path.join(tempfile.gettempdir(), 'subtitle_processor_scratch')
        os.makedirs(scratch_dir, exist_ok=True)
    
        # Use a predictable filename based on the video for easier debugging
        video_basename = os.path.splitext(os.path.basename(self.args.video_file))[0]
        temp_wav_file = os.path.join(scratch_dir, f"{video_basename}.wav")

        try:
            # --- Measure initial silence to compensate for silenceremove filter ---
            # This is done by measuring the audio duration before and after trimming.
            SILENCE_THRESHOLD = "-40dB"
            initial_silence_duration = 0.0

            # 1. Get original audio duration, ignoring potential stream errors.
            print("Analyzing original audio duration...", end='', flush=True)
            original_audio_duration = 0.0
            try:
                ffprobe_duration_cmd = [
                    'ffprobe', '-v', 'error', '-err_detect', 'ignore_err',
                    '-select_streams', 'a:0', '-show_entries', 'stream=duration',
                    '-of', 'json', self.args.video_file
                ]
                result = subprocess.run(ffprobe_duration_cmd, capture_output=True, text=True, check=True)
                original_duration_data = json.loads(result.stdout)
                if original_duration_data.get('streams') and 'duration' in original_duration_data['streams'][0]:
                    original_audio_duration = float(original_duration_data['streams'][0]['duration'])
                    print(f" [DONE - {original_audio_duration:.2f}s]")
                else:
                    # Fallback for streams without explicit duration metadata
                    _, _, container_duration = get_video_info(self.args.video_file)
                    original_audio_duration = container_duration
                    print(f" [DONE - Using container duration: {original_audio_duration:.2f}s]")
            except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
                print(" [FAILED]", file=sys.stderr)
                print(f"WARNING: Could not determine original audio duration: {e}. Timestamps may be inaccurate.", file=sys.stderr)

            # 2. Create the trimmed WAV file using -y to allow overwriting.
            ffmpeg_audio_extract_cmd = [
                'ffmpeg', '-nostdin', '-threads', '0', '-y',
                '-i', self.args.video_file,
                '-async', '1',  # Resample audio to match video timestamps, preventing drift
                '-vn', '-err_detect', 'ignore_err', '-f', 'wav', '-ac', '1',
                '-acodec', 'pcm_s16le', '-ar', '16000', '-af', f'silenceremove=start_periods=1:start_threshold={SILENCE_THRESHOLD}', temp_wav_file
            ]
            if self.verbose:
                print(f"\n  Running ffmpeg audio extraction command: {' '.join(ffmpeg_audio_extract_cmd)}")
            print(f"Preparing audio from '{self.args.video_file}' for debugging in '{temp_wav_file}'...", end='', flush=True)
            # Use text=True to get stdout/stderr as strings
            result = subprocess.run(ffmpeg_audio_extract_cmd, check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(" [FAILED]", file=sys.stderr)
                print(f"\nCRITICAL ERROR: Audio preparation failed. ffmpeg returned non-zero exit code.", file=sys.stderr)
                print(f"ffmpeg stderr:\n{result.stderr}", file=sys.stderr)
                sys.exit(1)
            print(" [DONE]")

            # 3. Get trimmed audio duration and calculate the offset
            if original_audio_duration > 0:
                print("Analyzing trimmed audio duration...", end='', flush=True)
                try:
                    ffprobe_trimmed_cmd = [
                        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'json', temp_wav_file
                    ]
                    result = subprocess.run(ffprobe_trimmed_cmd, capture_output=True, text=True, check=True)
                    trimmed_duration_data = json.loads(result.stdout)
                    trimmed_audio_duration = float(trimmed_duration_data['format']['duration'])
                    initial_silence_duration = original_audio_duration - trimmed_audio_duration
                    print(f" [DONE - {trimmed_audio_duration:.2f}s. Offset: {initial_silence_duration:.2f}s]")
                except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
                    print(f"WARNING: Could not determine trimmed audio duration: {e}. Timestamps may be inaccurate.", file=sys.stderr)

            print(f"Starting Whisper transcription...", flush=True)
            whisper_cli_args = [
                'whisper-cli', '-m', self.args.whisper_model,
                '-tr', '-osrt', # Always translate to English and output an SRT file.
                '-f', temp_wav_file, '-t', '8'
            ]
            # Add any extra user-provided parameters
            if self.args.whisper_params:
                print(f"Applying custom Whisper parameters: {self.args.whisper_params}")
                whisper_cli_args.extend(self.args.whisper_params.split())
            
            if self.verbose:
                print(f"  Running whisper-cli command: {' '.join(whisper_cli_args)}")

            # Capture output to provide better error messages
            result = subprocess.run(whisper_cli_args, capture_output=True, text=True)

            if result.returncode == 0:
                print("Whisper transcription complete.", flush=True)
            else:
                # This will be caught by the except block below, which now has more context.
                raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)
            
            temp_srt_path = f"{temp_wav_file}.srt"
            if os.path.exists(temp_srt_path):
                shutil.move(temp_srt_path, generated_srt_path)
            else:
                raise FileNotFoundError(f"Whisper-cli did not produce the expected output file: {temp_srt_path}")

            print("Filtering and tagging generated SRT file...", end='', flush=True)
            with open(generated_srt_path, 'r', encoding='utf-8') as f:
                subs = list(srt.parse(f.read()))

            # Adjust timestamps if we removed initial silence
            if initial_silence_duration > 0:
                print(f"Adjusting all subtitle timestamps by +{initial_silence_duration:.2f}s to compensate for removed silence...", end='', flush=True)
                offset = datetime.timedelta(seconds=initial_silence_duration)
                for sub in subs:
                    sub.start += offset
                    sub.end += offset
            if not subs:
                print(" [WARNING: WHISPER GENERATED EMPTY SRT]", flush=True)
                if os.path.exists(temp_wav_file):
                    os.remove(temp_wav_file)
                return generated_srt_path

            filtered_subs = [subs[0]] if subs else []
            for i in range(1, len(subs)):
                if subs[i].content.strip() != subs[i-1].content.strip():
                    filtered_subs.append(subs[i])
            
            num_removed = len(subs) - len(filtered_subs)
            print(f" [DONE - Filtered {num_removed} duplicates]" if num_removed > 0 else " [DONE]")

            sentinel = srt.Subtitle(index=0, start=datetime.timedelta(seconds=0), end=datetime.timedelta(seconds=3), content="AI Captioning by Whisper.cpp, courtesy of Georgi Gerganov")
            final_subs = [sentinel] + filtered_subs

            # --- Sparse Subtitle Check ---
            if original_audio_duration > 0:
                duration_minutes = original_audio_duration / 60
                subs_per_minute = len(final_subs) / duration_minutes if duration_minutes > 0 else 0
                # Warn if there's less than 1 subtitle every 3 minutes on average, for videos longer than 2 minutes.
                SPARSE_THRESHOLD = 1/3
                if duration_minutes > 2 and subs_per_minute < SPARSE_THRESHOLD:
                    print(f"\nWARNING: Generated subtitle count is unusually low ({len(final_subs)} subs for a {duration_minutes:.1f} min video).")
                    print("         This can happen with non-English dialogue or high background noise.")
                    print("         Consider using --whisper-params to specify the language (e.g., '--whisper-params \"-l th\"' for Thai).")

            with open(generated_srt_path, 'w', encoding='utf-8') as f:
                f.write(srt.compose(final_subs))
            print(f"SRT file processed successfully: {generated_srt_path}", flush=True)
            
            # Clean up the intermediate WAV file on success
            if os.path.exists(temp_wav_file):
                os.remove(temp_wav_file)

            return generated_srt_path

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # On failure, intermediate files in /tmp/subtitle_processor_scratch are NOT removed, allowing for debugging.
            print(" [FAILED]", file=sys.stderr)
            
            # Provide detailed error from stderr if available
            if isinstance(e, subprocess.CalledProcessError) and e.stderr:
                print(f"\nERROR: Subtitle generation failed. whisper-cli returned non-zero exit status {e.returncode}.", file=sys.stderr)
                print("\n--- Whisper-cli Error Log ---", file=sys.stderr)
                print(e.stderr.strip(), file=sys.stderr)
                print("--- End of Whisper-cli Error Log ---", file=sys.stderr)
            else:
                # Fallback for other errors like FileNotFoundError
                print(f"\nERROR: Subtitle generation failed: {e}", file=sys.stderr)

            print(f"\nDebug files may be available in: {scratch_dir}", file=sys.stderr)
            sys.exit(1)

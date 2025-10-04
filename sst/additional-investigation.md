1) Parakeet
2) Dialarization

See below some collected resources:

---
https://www.reddit.com/r/LocalLLaMA/comments/1nf10ye/30_days_testing_parakeet_v3_vs_whisper/

30 Days Testing Parakeet v3 vs Whisper
Discussion
MacOS dev here who just went through integration with Parakeet v3, also known as parakeet-tdt-0.6b-v3 for dictation and meeting recordings purposes, including speaker identification. I was not alone, it was a team work.

Foreword
Parakeet v3 supported languages are:

Bulgarian (bg), Croatian (hr), Czech (cs), Danish (da), Dutch (nl), English (en), Estonian (et), Finnish (fi), French (fr), German (de), Greek (el), Hungarian (hu), Italian (it), Latvian (lv), Lithuanian (lt), Maltese (mt), Polish (pl), Portuguese (pt), Romanian (ro), Slovak (sk), Slovenian (sl), Spanish (es), Swedish (sv), Russian (ru), Ukrainian (uk)

Long story short: very europe / latin-based languages focus so if you are looking for Chinese, Japanese, Korean, Arabic, Hindi, etc, you are out of luck sorry.

(More details on HF)

The Speed Thing Everyone's Talking About
Holy s***, this thing is fast.

We're talking an average of 10x faster than Whisper. Rule of thumb: 30 seconds per hour of audio to transcribe, allowing for real-time transcription and processing of hours-long files.

What Actually Works Well
A bit less accurate than Whisper but so fast

English and French (our main languages) work great

Matches big Whisper models for general discussion in term of accuracy

Perfect for meeting notes, podcast transcripts, that kind of stuff

Play well with Pyannote for diarization

Actually tells people apart in most scenarios

Close to Deepgram Nova (our TTS cloud provider) in terms of accuracy

Most of our work went here to get accuracy and speed at this level

Where It Falls Apart
No custom dictionary support

This one's a killer for specialized content

Struggles with acronyms, company names, technical terms, french accents ;). The best example here is trying to dictate "Parakeet," which it usually writes down as "Parakit."

Can't teach it your domain-specific vocabulary

-> You need some LLM post-processing to clean up or improve it here.

Language support is... optimistic

Claims 25 languages, but quality is all over the map

Tested Dutch with a colleague - results were pretty rough

Feels like they trained some languages way better than others

Speaker detection is hard

Gets close to perfect with PYAnnote but...

You'll have a very hard time with overlapping speakers and the number of speakers detected.

Plus, fusing timings/segments to get a proper transcript, but overall results are better with Parakeet than Whisper.

Speech-to-text tech is now good enough on local
Speech-to-text for normal use cases is solved now. Whether you use Parakeet or big Whisper models, you can get totally usable results in real-time with speaker ID.

But we've also hit this plateau where having 95% accuracy feels impossible.

This is especially true for having exact timecodes associated with speakers and clean diarization when two or more people speak at the same time.

The good news: it will only get better, as shown with the new Precision-2 model from PYAnnote.

Our learnings so far:
If you need "good enough" transcripts (meetings, content creation, pulling topics): Parakeet v3 is fantastic. Fast, local, gets the job done.

If you are processing long audio files and/or in batches: Parakeet is really great too and as fast as cloud.

If you need every single word perfect (legal, medical, compliance): You're probably still stuck with slower, more careful approaches using Whisper or closed cloud models. The plateau is real.

For dictation, especially long text, you still need a LLM post process to clean out the content and do clean formatting

So Parakeet or Whisper? Actually both.
Whisper's the Swiss Army knife: slower but handles edge cases (with dictionnary) and supports more languages.

Parakeet is the race car: stupid fast when the conditions are right. (and you want to transcribe an european language)

Most of us probably need both depending on the job.

Conclusion
If you're building something where the transcript is just the starting point (topic extraction, summarization, content creation), Parakeet v3 is killer.

If you're in a "every word matters" situation, you might be waiting a bit longer for the tech to catch up.

Anyone else playing with that stack? What's your experience? Also if you want to get more technical, feel free to ask any questions in the comments.

Implementation Notes
We used Argmax's WhisperKit, both open-source and proprietary versions: https://github.com/argmaxinc/WhisperKit They have an optimized version of the models, both in size and battery impact, and SpeakerKit, their diarization engine is fast.

New kid on the block worth checking out: https://github.com/FluidInference/FluidAudio

This also looks promising: https://github.com/Blaizzy/mlx-audio

Benchmarks
OpenASR Leaderboard (with multilingual benchmarks): https://huggingface.co/spaces/hf-audio/open_asr_leaderboard

Argmax real-time transcription benchmarks: https://github.com/argmaxinc/OpenBench/blob/main/BENCHMARKS.md#real-time-transcription

Fluid Parakeet V3 benchmark: https://github.com/FluidInference/FluidAudio/blob/main/Documentation/Benchmarks.md


---
https://github.com/FluidInference/FluidAudio/blob/main/Documentation/SpeakerDiarization.md

# Speaker Diarization

Real-time speaker diarization for iOS and macOS, answering "who spoke when" in audio streams.

## Quick Start

```swift
import FluidAudio

// 1. Download models (one-time setup)
let models = try await DiarizerModels.downloadIfNeeded()

// 2. Initialize with default config
let diarizer = DiarizerManager()
diarizer.initialize(models: models)

// 3. Normalize any audio file to 16kHz mono Float32 using AudioConverter
let converter = AudioConverter()
let url = URL(fileURLWithPath: "path/to/audio.wav")
let audioSamples = try converter.resampleAudioFile(url)

// 4. Run diarization (accepts any RandomAccessCollection<Float>)
let result = try diarizer.performCompleteDiarization(audioSamples)

// Alternative: Use ArraySlice for zero-copy processing
let audioSlice = audioSamples[1000..<5000]  // No memory copy!
let sliceResult = try diarizer.performCompleteDiarization(audioSlice)

// 5. Get results
for segment in result.segments {
    print("Speaker \(segment.speakerId): \(segment.startTimeSeconds)s - \(segment.endTimeSeconds)s")
}
```

## Manual Model Loading

If you deploy in an offline environment, stage the Core ML bundles manually and skip the automatic HuggingFace downloader.

### Required assets

Download the two `.mlmodelc` folders from `FluidInference/speaker-diarization-coreml`:

- `pyannote_segmentation.mlmodelc`
- `wespeaker_v2.mlmodelc`

Keep the folder names unchanged so the loader can find `coremldata.bin` inside each bundle.

### Folder layout

Place the staged repo in persistent storage (replace `/opt/models` with your path):

```
/opt/models
└── speaker-diarization-coreml
    ├── pyannote_segmentation.mlmodelc
    │   ├── coremldata.bin
    │   └── ...
    └── wespeaker_v2.mlmodelc
        ├── coremldata.bin
        └── ...
```

You can clone with Git LFS, download the `.tar` archives from HuggingFace, or copy the directory from a machine that already ran `DiarizerModels.downloadIfNeeded()` (macOS cache: `~/Library/Application Support/FluidAudio/Models/speaker-diarization-coreml`).

### Loading without downloads

Point `DiarizerModels.load` at the staged bundles and initialize the manager with the returned models:

```swift
import FluidAudio

@main
struct OfflineDiarizer {
    static func main() async {
        do {
            let basePath = "/opt/models/speaker-diarization-coreml"
            let segmentation = URL(fileURLWithPath: basePath).appendingPathComponent("pyannote_segmentation.mlmodelc")
            let embedding = URL(fileURLWithPath: basePath).appendingPathComponent("wespeaker_v2.mlmodelc")

            let models = try await DiarizerModels.load(
                localSegmentationModel: segmentation,
                localEmbeddingModel: embedding
            )

            let diarizer = DiarizerManager()
            diarizer.initialize(models: models)

            // ... run diarization as usual
        } catch {
            print("Failed to load diarizer models: \(error)")
        }
    }
}
```

Use `FileManager` to verify the two `.mlmodelc` folders exist before loading. When paths are correct, the loader never contacts the network and no auto-download occurs.

### Custom Configuration (Optional)

For fine-tuning, you can customize the configuration:
```swift
let config = DiarizerConfig(
    clusteringThreshold: 0.7,  // Speaker separation sensitivity (0.5-0.9)
    minSpeechDuration: 1.0,     // Minimum speech segment (seconds)
    minSilenceGap: 0.5          // Minimum gap between speakers (seconds)
)
let diarizer = DiarizerManager(config: config)
```

## Streaming/Real-time Processing

Process audio in chunks for real-time applications:

```swift
// Configure for streaming
let diarizer = DiarizerManager()  // Default config works well
diarizer.initialize(models: models)

let chunkDuration = 5.0  // Can be 3.0 for low latency or 10.0 for best accuracy
let chunkSize = Int(16000 * chunkDuration)  // Convert to samples
var audioBuffer: [Float] = []
var streamPosition = 0.0

for audioSamples in audioStream {
    audioBuffer.append(contentsOf: audioSamples)

    // Process when we have accumulated enough audio
    while audioBuffer.count >= chunkSize {
        let chunk = Array(audioBuffer.prefix(chunkSize))
        audioBuffer.removeFirst(chunkSize)

        // This works with any chunk size, but accuracy varies
        let result = try diarizer.performCompleteDiarization(chunk)

        // Adjust timestamps manually
        for segment in result.segments {
            let adjustedSegment = TimedSpeakerSegment(
                speakerId: segment.speakerId,
                startTimeSeconds: streamPosition + segment.startTimeSeconds,
                endTimeSeconds: streamPosition + segment.endTimeSeconds
            )
            handleSpeakerSegment(adjustedSegment)
        }

        streamPosition += chunkDuration
    }
}
```

Notes:

- Keep one `DiarizerManager` instance per stream so `SpeakerManager` maintains ID consistency.
- Always rebase per-chunk timestamps by `(chunkStartSample / sampleRate)`.
- Provide 16 kHz mono Float32 samples; pad final chunk to the model window.
- Tune `speakerThreshold` and `embeddingThreshold` to trade off ID stability vs. sensitivity.

**Speaker Enrollment:** The `Speaker` class includes a `name` field for enrollment workflows. When users introduce themselves ("My name is Alice"), update the speaker's name from the default (e.g. "Speaker_1") to enable personalized identification.

### Chunk Size Considerations

The `performCompleteDiarization` function accepts audio of any length, but accuracy varies:

- **< 3 seconds**: May fail or produce unreliable results
- **3-5 seconds**: Minimum viable chunk, reduced accuracy
- **10 seconds**: Optimal balance of accuracy and latency (recommended)
- **> 10 seconds**: Good accuracy but higher latency
- **Maximum**: Limited only by memory

You can adjust chunk size based on your needs:
- **Low latency**: Use 3-5 second chunks (accept lower accuracy)
- **High accuracy**: Use 10+ second chunks (accept higher latency)

The diarizer doesn't automatically chunk audio - you need to:
1. Accumulate incoming audio samples to your desired chunk size
2. Process chunks with `performCompleteDiarization`
3. Maintain speaker IDs across chunks using `SpeakerManager`

### Real-time Audio Capture Example

```swift
import AVFoundation

class RealTimeDiarizer {
    private let audioEngine = AVAudioEngine()
    private let diarizer: DiarizerManager
    private var audioBuffer: [Float] = []
    private let chunkDuration = 10.0  // seconds
    private let sampleRate: Double = 16000
    private var chunkSamples: Int { Int(sampleRate * chunkDuration) }
    private var streamPosition: Double = 0
    // Audio converter for format conversion
    private let converter = AudioConverter()
    
    init() async throws {
        let models = try await DiarizerModels.downloadIfNeeded()
        diarizer = DiarizerManager()  // Default config
        diarizer.initialize(models: models)
    }

    func startCapture() throws {
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)

        // Install tap to capture audio
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { [weak self] buffer, _ in
            guard let self = self else { return }

            // Convert to 16kHz mono Float array using AudioConverter (streaming)
            if let samples = try? self.converter.resampleBuffer(buffer) {
                self.processAudioSamples(samples)
            }
        }

        audioEngine.prepare()
        try audioEngine.start()
    }

    private func processAudioSamples(_ samples: [Float]) {
        audioBuffer.append(contentsOf: samples)

        // Process complete chunks
        while audioBuffer.count >= chunkSamples {
            let chunk = Array(audioBuffer.prefix(chunkSamples))
            audioBuffer.removeFirst(chunkSamples)

            Task {
                do {
                    let result = try diarizer.performCompleteDiarization(chunk)
                    await handleResults(result, at: streamPosition)
                    streamPosition += chunkDuration
                } catch {
                    print("Diarization error: \(error)")
                }
            }
        }
    }

    @MainActor
    private func handleResults(_ result: DiarizationResult, at position: Double) {
        for segment in result.segments {
            print("Speaker \(segment.speakerId): \(position + segment.startTimeSeconds)s")
        }
    }

    private func convertBuffer(_ buffer: AVAudioPCMBuffer) -> [Float] {
        // Use FluidAudio.AudioConverter in streaming mode
        // Returns 16kHz mono Float array; swallow conversion errors in sample code
        return (try? converter.resampleBuffer(buffer)) ?? []
    }
}
```

## Core Components

### DiarizerManager
Main entry point for diarization pipeline:
```swift
let diarizer = DiarizerManager()  // Default config (recommended)
diarizer.initialize(models: models)

// Normalize with AudioConverter
let samples = try AudioConverter().resampleAudioFile(URL(fileURLWithPath: "path/to/audio.wav"))
let result = try diarizer.performCompleteDiarization(samples)
```

### SpeakerManager
Tracks speaker identities across audio chunks:
```swift
let speakerManager = diarizer.speakerManager

// Get speaker information
print("Active speakers: \(speakerManager.speakerCount)")
for speakerId in speakerManager.speakerIds {
    if let speaker = speakerManager.getSpeaker(for: speakerId) {
        print("\(speaker.name): \(speaker.duration)s total")
    }
}
```

### DiarizerConfig
Configuration parameters:
```swift
let config = DiarizerConfig(
    clusteringThreshold: 0.7,      // Speaker separation threshold (0.0-1.0)
    minSpeechDuration: 1.0,         // Minimum speech duration in seconds
    minSilenceGap: 0.5,             // Minimum silence between speakers
    minActiveFramesCount: 10.0,     // Minimum active frames for valid segment
    debugMode: false                // Enable debug logging
)
```

## Known Speaker Recognition

Pre-load known speaker profiles:

```swift
// Create embeddings for known speakers
let aliceAudio = loadAudioFile("alice_sample.wav")
let aliceEmbedding = try diarizer.extractEmbedding(aliceAudio)

// Initialize with known speakers
let alice = Speaker(id: "Alice", name: "Alice", currentEmbedding: aliceEmbedding)
let bob = Speaker(id: "Bob", name: "Bob", currentEmbedding: bobEmbedding)
speakerManager.initializeKnownSpeakers([alice, bob])

// Process - will use "Alice" instead of "Speaker_1" when matched
let result = try diarizer.performCompleteDiarization(audioSamples)
```

## SwiftUI Integration

```swift
import SwiftUI
import FluidAudio

struct DiarizationView: View {
    @StateObject private var processor = DiarizationProcessor()

    var body: some View {
        VStack {
            Text("Speakers: \(processor.speakerCount)")

            List(processor.activeSpeakers) { speaker in
                HStack {
                    Circle()
                        .fill(speaker.isSpeaking ? Color.green : Color.gray)
                        .frame(width: 10, height: 10)
                    Text(speaker.name)
                    Spacer()
                    Text("\(speaker.duration, specifier: "%.1f")s")
                }
            }

            Button(processor.isProcessing ? "Stop" : "Start") {
                processor.toggleProcessing()
            }
        }
    }
}

@MainActor
class DiarizationProcessor: ObservableObject {
    @Published var speakerCount = 0
    @Published var activeSpeakers: [SpeakerDisplay] = []
    @Published var isProcessing = false

    private var diarizer: DiarizerManager?

    func toggleProcessing() {
        if isProcessing {
            stopProcessing()
        } else {
            startProcessing()
        }
    }

    private func startProcessing() {
        Task {
            let models = try await DiarizerModels.downloadIfNeeded()
            diarizer = DiarizerManager()  // Default config
            diarizer?.initialize(models: models)
            isProcessing = true

            // Start audio capture and process chunks
            AudioCapture.start { [weak self] chunk in
                self?.processChunk(chunk)
            }
        }
    }

    private func processChunk(_ audio: [Float]) {
        Task { @MainActor in
            guard let diarizer = diarizer else { return }

            let result = try diarizer.performCompleteDiarization(audio)
            speakerCount = diarizer.speakerManager.speakerCount

            // Update UI with current speakers
            activeSpeakers = diarizer.speakerManager.speakerIds.compactMap { id in
                guard let speaker = diarizer.speakerManager.getSpeaker(for: id) else {
                    return nil
                }
                return SpeakerDisplay(
                    id: id,
                    name: speaker.name,
                    duration: speaker.duration,
                    isSpeaking: result.segments.contains { $0.speakerId == id }
                )
            }
        }
    }
}
```

## Performance Optimization

```swift
let config = DiarizerConfig(
    clusteringThreshold: 0.7,
    minSpeechDuration: 1.0,
    minSilenceGap: 0.5
)

// Lower latency for real-time
let config = DiarizerConfig(
    clusteringThreshold: 0.7,
    minSpeechDuration: 0.5,    // Faster response
    minSilenceGap: 0.3         // Quicker speaker switches
)
```

### Memory Management
```swift
// Reset between sessions to free memory
diarizer.speakerManager.reset()

// Or cleanup completely
diarizer.cleanup()
```

## Benchmarking

Evaluate performance on your audio:

```bash
# Command-line benchmark
swift run fluidaudio diarization-benchmark --single-file ES2004a

# Results:
# DER: 17.7% (Miss: 10.3%, FA: 1.6%, Speaker Error: 5.8%)
# RTFx: 141.2x (real-time factor) M1 2022
```

## API Reference

### DiarizerManager

| Method | Description |
|--------|-------------|
| `initialize(models:)` | Initialize with Core ML models |
| `performCompleteDiarization(_:sampleRate:)` | Process audio and return segments |
| `cleanup()` | Release resources |

### SpeakerManager

| Method | Description |
|--------|-------------|
| `assignSpeaker(_:speechDuration:)` | Assign embedding to speaker |
| `initializeKnownSpeakers(_:)` | Load known speaker profiles |
| `getSpeaker(for:)` | Get speaker details |
| `reset()` | Clear all speakers |

### DiarizationResult

| Property | Type | Description |
|----------|------|-------------|
| `segments` | `[TimedSpeakerSegment]` | Speaker segments with timing |
| `speakerDatabase` | `[String: [Float]]?` | Speaker embeddings (debug mode) |
| `timings` | `PipelineTimings?` | Processing timings (debug mode) |

## Requirements

- iOS 16.0+ / macOS 13.0+
- Swift 5.9+
- ~100MB for Core ML models (downloaded on first use)

## Performance

| Device | RTFx | Notes |
|--------|------|-------|
| M2 MacBook Air | 150x | Apple Neural Engine |
| M1 iPad Pro | 120x | Neural Engine |
| iPhone 14 Pro | 80x | Neural Engine |
| GitHub Actions | 140x | CPU only |

## Troubleshooting

### High DER on certain audio
- Check if audio has overlapping speech (not yet supported)
- Ensure 16kHz sampling rate
- Verify audio isn't too noisy

### Memory issues
- Call `reset()` between sessions
- Process shorter chunks for streaming
- Reduce `minActiveFramesCount` if needed

### Model download fails
- Check internet connection
- Verify ~100MB free space
- Models cached after first download

## License

See main repository LICENSE file.

# Benchmarks

2024 MacBook Pro, 48GB Ram, M4 Pro, Tahoe 26.0

## Transcription

https://huggingface.co/FluidInference/parakeet-tdt-0.6b-v3-coreml 

```bash
swift run fluidaudio fleurs-benchmark --languages en_us,it_it,es_419,fr_fr,de_de,ru_ru,uk_ua --samples all
```

```text
[01:58:26.666] [INFO] [FLEURSBenchmark] ================================================================================
[01:58:26.666] [INFO] [FLEURSBenchmark] FLEURS BENCHMARK SUMMARY
[01:58:26.666] [INFO] [FLEURSBenchmark] ================================================================================
[01:58:26.666] [INFO] [FLEURSBenchmark]
[01:58:26.666] [INFO] [FLEURSBenchmark] Language                  | WER%   | CER%   | RTFx    | Duration | Processed | Skipped
[01:58:26.666] [INFO] [FLEURSBenchmark] -----------------------------------------------------------------------------------------
[01:58:26.666] [INFO] [FLEURSBenchmark] English (US)              | 5.7    | 2.8    | 197.8   | 3442.9s  | 350       | -
[01:58:26.666] [INFO] [FLEURSBenchmark] French (France)           | 6.3    | 3.0    | 191.3   | 560.8s   | 52        | 298
[01:58:26.667] [INFO] [FLEURSBenchmark] German (Germany)          | 3.1    | 1.2    | 216.7   | 62.1s    | 5         | -
[01:58:26.667] [INFO] [FLEURSBenchmark] Italian (Italy)           | 4.3    | 2.0    | 213.5   | 743.3s   | 50        | -
[01:58:26.667] [INFO] [FLEURSBenchmark] Russian (Russia)          | 7.8    | 2.8    | 186.3   | 621.2s   | 50        | -
[01:58:26.667] [INFO] [FLEURSBenchmark] Spanish (Spain)           | 5.6    | 2.7    | 214.6   | 586.9s   | 50        | -
[01:58:26.667] [INFO] [FLEURSBenchmark] Ukrainian (Ukraine)       | 7.2    | 2.1    | 192.8   | 528.2s   | 50        | -
[01:58:26.667] [INFO] [FLEURSBenchmark] -----------------------------------------------------------------------------------------
[01:58:26.667] [INFO] [FLEURSBenchmark] AVERAGE                   | 5.7    | 2.4    | 201.9   | 6545.5s  | 607       | 298
```

```text
[02:01:49.655] [INFO] [Benchmark] 2620 files per dataset • Test runtime: 3m 2s • 09/25/2025, 2:01 AM EDT
[02:01:49.655] [INFO] [Benchmark] --- Benchmark Results ---
[02:01:49.655] [INFO] [Benchmark]    Dataset: librispeech test-clean
[02:01:49.655] [INFO] [Benchmark]    Files processed: 2620
[02:01:49.655] [INFO] [Benchmark]    Average WER: 2.6%
[02:01:49.655] [INFO] [Benchmark]    Median WER: 0.0%
[02:01:49.655] [INFO] [Benchmark]    Average CER: 1.1%
[02:01:49.655] [INFO] [Benchmark]    Median RTFx: 137.8x
[02:01:49.655] [INFO] [Benchmark]    Overall RTFx: 153.4x (19452.5s / 126.8s)
[02:01:49.655] [INFO] [Benchmark] Results saved to: asr_benchmark_results.json
[02:01:49.655] [INFO] [Benchmark] ASR benchmark completed successfully
```

`swift run fluidaudio asr-benchmark --max-files all --model-version v2`

Use v2 if you only need English, it is a bit more accurate

```text
ansient day, like music in the air. Ah
[01:35:16.880] [INFO] [Benchmark] File: 908-157963-0010.flac (WER: 15.4%) (Duration: 6.28s)
[01:35:16.880] [INFO] [Benchmark] ------------------------------------------------------------
[01:35:16.894] [INFO] [Benchmark] Normalized Reference: she ceasd and smild in tears then sat down in her silver shrine
[01:35:16.894] [INFO] [Benchmark] Normalized Hypothesis:        she ceased and smiled in tears then sat down in her silver shrine
[01:35:16.894] [INFO] [Benchmark] Original Hypothesis:  She ceased and smiled in tears, Then sat down in her silver shrine,
[01:35:16.894] [INFO] [Benchmark] 2620 files per dataset • Test runtime: 3m 25s • 09/26/2025, 1:35 AM EDT
[01:35:16.894] [INFO] [Benchmark] --- Benchmark Results ---
[01:35:16.894] [INFO] [Benchmark]    Dataset: librispeech test-clean
[01:35:16.894] [INFO] [Benchmark]    Files processed: 2620
[01:35:16.894] [INFO] [Benchmark]    Average WER: 2.2%
[01:35:16.894] [INFO] [Benchmark]    Median WER: 0.0%
[01:35:16.894] [INFO] [Benchmark]    Average CER: 0.7%
[01:35:16.894] [INFO] [Benchmark]    Median RTFx: 125.6x
[01:35:16.894] [INFO] [Benchmark]    Overall RTFx: 141.2x (19452.5s / 137.7s)
[01:35:16.894] [INFO] [Benchmark] Results saved to: asr_benchmark_results.json
[01:35:16.894] [INFO] [Benchmark] ASR benchmark completed successfully
```

### ASR Model Compilation

Core ML first-load compile times captured on iPhone 16 Pro Max and iPhone 13 running the
parakeet-tdt-0.6b-v3-coreml bundle. Cold-start compilation happens the first time each Core ML model
is loaded; subsequent loads hit the cached binaries. Warm compile metrics were collected only on the
iPhone 16 Pro Max run, and only for models that were reloaded during the session.

| Model         | iPhone 16 Pro Max cold (ms) | iPhone 16 Pro Max warm (ms) | iPhone 13 cold (ms) | Compute units               |
| ------------- | --------------------------: | ---------------------------: | ------------------: | --------------------------- |
| Preprocessor  |                        9.15 |                           - |              632.63 | MLComputeUnits(rawValue: 2) |
| Encoder       |                     3361.23 |                      162.05 |             4396.00 | MLComputeUnits(rawValue: 1) |
| Decoder       |                       88.49 |                        8.11 |              146.01 | MLComputeUnits(rawValue: 1) |
| JointDecision |                       48.46 |                        7.97 |               71.85 | MLComputeUnits(rawValue: 1) |

## Voice Activity Detection

Model is nearly identical to the base model in terms of quality, perforamnce wise we see an up to ~3.5x improvement compared to the silero Pytorch VAD model with the 256ms batch model (8 chunks of 32ms)

![VAD/speed.png](VAD/speed.png)
![VAD/correlation.png](VAD/correlation.png)

Dataset: https://github.com/Lab41/VOiCES-subset

```text
swift run fluidaudio vad-benchmark --dataset voices-subset --all-files --threshold 0.85
...
Timing Statistics:
[18:56:31.208] [INFO] [VAD]    Total processing time: 0.29s
[18:56:31.208] [INFO] [VAD]    Total audio duration: 351.05s
[18:56:31.208] [INFO] [VAD]    RTFx: 1230.6x faster than real-time
[18:56:31.208] [INFO] [VAD]    Audio loading time: 0.00s (0.6%)
[18:56:31.208] [INFO] [VAD]    VAD inference time: 0.28s (98.7%)
[18:56:31.208] [INFO] [VAD]    Average per file: 0.011s
[18:56:31.208] [INFO] [VAD]    Min per file: 0.001s
[18:56:31.208] [INFO] [VAD]    Max per file: 0.020s
[18:56:31.208] [INFO] [VAD]
VAD Benchmark Results:
[18:56:31.208] [INFO] [VAD]    Accuracy: 96.0%
[18:56:31.208] [INFO] [VAD]    Precision: 100.0%
[18:56:31.208] [INFO] [VAD]    Recall: 95.8%
[18:56:31.208] [INFO] [VAD]    F1-Score: 97.9%
[18:56:31.208] [INFO] [VAD]    Total Time: 0.29s
[18:56:31.208] [INFO] [VAD]    RTFx: 1230.6x faster than real-time
[18:56:31.208] [INFO] [VAD]    Files Processed: 25
[18:56:31.208] [INFO] [VAD]    Avg Time per File: 0.011s
```

```text
swift run fluidaudio vad-benchmark --dataset musan-full --num-files all --threshold 0.8
...
[23:02:35.539] [INFO] [VAD] Total processing time: 322.31s
[23:02:35.539] [INFO] [VAD] Timing Statistics:
[23:02:35.539] [INFO] [VAD] RTFx: 1220.7x faster than real-time
[23:02:35.539] [INFO] [VAD] Audio loading time: 1.20s (0.4%)
[23:02:35.539] [INFO] [VAD] VAD inference time: 319.57s (99.1%)
[23:02:35.539] [INFO] [VAD] Average per file: 0.160s
[23:02:35.539] [INFO] [VAD] Total audio duration: 393442.58s
[23:02:35.539] [INFO] [VAD] Min per file: 0.000s
[23:02:35.539] [INFO] [VAD] Max per file: 0.873s
[23:02:35.711] [INFO] [VAD] VAD Benchmark Results:
[23:02:35.711] [INFO] [VAD] Accuracy: 94.2%
[23:02:35.711] [INFO] [VAD] Precision: 92.6%
[23:02:35.711] [INFO] [VAD] Recall: 78.9%
[23:02:35.711] [INFO] [VAD] F1-Score: 85.2%
[23:02:35.711] [INFO] [VAD] Total Time: 322.31s
[23:02:35.711] [INFO] [VAD] RTFx: 1220.7x faster than real-time
[23:02:35.711] [INFO] [VAD] Files Processed: 2016
[23:02:35.711] [INFO] [VAD] Avg Time per File: 0.160s
[23:02:35.744] [INFO] [VAD] Results saved to: vad_benchmark_results.json
```


## Speaker Diarization

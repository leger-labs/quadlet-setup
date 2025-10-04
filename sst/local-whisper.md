## Description

speech to text locally running optimized, adapted SST local llm which gets piped to openwebui. advanced/eventual improvement is a backend that would also run dialarization and chat summarization so that this can all be done from within the owui instance; make sure that for basic/default whisper model we actually leverage ramalama

we draw inspiration from the harbor implementation:
https://github.com/search?q=repo%3Aav%2Fharbor%20whisper&type=code
https://www.reddit.com/r/LocalLLaMA/comments/1how0lc/how_can_i_set_up_whispercpp_on_a_machine_that_has/
as it already has a clear implementation plan in harbor.

maybe this gist can be useful:
https://gist.github.com/FNGarvin/90e48055a61bf1fd08f9e2625e427226
found on gh issue discussing w


## Implementation Notes

Different models: parakeet v3 with dialarization https://www.reddit.com/r/LocalLLaMA/comments/1nf10ye/30_days_testing_parakeet_v3_vs_whisper/ https://github.com/FluidInference/FluidAudio/blob/main/Documentation/SpeakerDiarization.md

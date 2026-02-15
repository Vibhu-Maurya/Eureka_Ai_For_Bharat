# Design Document: AI Video Orchestration & Personalization Engine

## Overview

Multi-agent system transforming text + optional media into short videos via iterative refinement. Core loop: Draft → Critique → Refine. Inspired by SciTalk, PhyT2V, MMCTAgent, and UniVA research. Emphasizes Indic language support for "AI for Bharat" hackathon.

## Architecture

Four agents coordinated by Central Orchestrator: **Planner** (breaks content into scenes with scripts) → **Executor** (generates visuals via Veo/Runway, audio via AWS Polly/HuggingFace Indic TTS, captions) → **Critic** (scores semantic alignment, pacing, visual quality, scene cohesion) → **Replanner** (refines prompts for flagged scenes). Loop continues until quality threshold met or max iterations reached.

**Tech Stack:** Python 3.11+, LangChain/LlamaIndex for agents, GPT-4/Claude for LLM, FFmpeg for video assembly, Hypothesis for property testing, Pydantic for data models.

## Components and Interfaces

**Core Data Models:** InputContent (text + optional media), Scene (script, duration, visual_description, asset URLs), ScenePlan (list of scenes), MediaAsset (video/audio/caption files), QualityScore (0-1 scores per dimension), QualityReport (scores + scene feedback), RefinementPlan (targeted regeneration actions).

**Agent Interfaces:** Each agent has single primary method - Planner.plan() → ScenePlan, Executor.execute_plan() → MediaAssets, Critic.critique() → QualityReport, Replanner.replan() → RefinementPlan. VideoAssembler.assemble() combines assets using FFmpeg.

**Service Adapters:** Abstract adapters for VideoGenerationAdapter (Veo/Runway), TTSAdapter (Polly/HuggingFace), TranscriptionAdapter (AWS Transcribe). Enables easy mocking and service swapping.


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Input Processing Properties

**Property 1: Text input acceptance**
*For any* non-empty text string, the system should accept and parse it successfully, returning a valid InputContent object.
**Validates: Requirements 1.1**

**Property 2: Media reference storage**
*For any* valid image or video file reference provided alongside text, the system should store the reference and make it available for scene processing.
**Validates: Requirements 1.2, 1.3**

**Property 3: Text requirement validation**
*For any* input without text content, the system should reject it with a validation error, regardless of whether media files are present.
**Validates: Requirements 1.4**

**Property 4: Unsupported format error handling**
*For any* input containing unsupported file formats, the system should return a descriptive error message identifying the unsupported format.
**Validates: Requirements 1.5**

**Property 5: Input persistence round-trip**
*For any* valid InputContent object, storing it then retrieving it should produce an equivalent object with the same text, media references, and metadata.
**Validates: Requirements 1.6, 2.6**

### Planning Properties

**Property 6: Scene generation completeness**
*For any* valid input content, the Planner should generate a ScenePlan with at least one Scene, and each Scene should have non-empty script, visual description, and positive duration.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

### Media Generation Properties

**Property 7: Visual generation API invocation**
*For any* scene requiring visual generation (no user-provided media), the Executor should call the Video Generation API with a non-empty prompt derived from the scene's visual description.
**Validates: Requirements 3.1**

**Property 8: API response validation**
*For any* response from external APIs (video generation, TTS, transcription), the system should validate the response format before processing, rejecting malformed responses.
**Validates: Requirements 3.2, 10.8**

**Property 9: Retry logic for failures**
*For any* failed API call, the system should retry up to the configured maximum (e.g., 3 times) with appropriate delays before reporting an error.
**Validates: Requirements 3.3, 10.3**

**Property 10: User media preference**
*For any* scene with user-provided images or video, the Executor should use those assets rather than generating new visuals via API.
**Validates: Requirements 3.4**

**Property 11: Service adapter selection**
*For any* configured service (video generation, TTS, transcription), the system should route requests to the configured adapter based on configuration and language requirements.
**Validates: Requirements 3.6, 3.7, 4.2, 4.3, 10.5, 11.5, 11.6**

**Property 12: Media asset persistence**
*For any* successfully generated media asset (visual, audio, caption), the system should store it with correct scene association and metadata, making it retrievable for assembly.
**Validates: Requirements 3.5, 4.5**

**Property 13: Audio generation from script**
*For any* scene with a non-empty script, the Executor should generate audio via TTS with the specified language and voice parameters.
**Validates: Requirements 4.1, 4.4**

**Property 14: Audio generation error handling**
*For any* audio generation failure, the system should return a descriptive error and halt processing for that scene.
**Validates: Requirements 4.6**

### Caption Generation Properties

**Property 15: Caption generation from audio**
*For any* scene with generated or transcribed audio, the system should generate synchronized captions.
**Validates: Requirements 5.1, 5.5**

**Property 16: Caption format compliance**
*For any* generated caption file, it should conform to standard subtitle format specifications (e.g., SRT format with proper timing markers).
**Validates: Requirements 5.3**

**Property 17: Transcription for user video**
*For any* user-provided video containing audio, the Transcription Service should be invoked to generate a text transcript.
**Validates: Requirements 5.4**

### Video Assembly Properties

**Property 18: Complete asset assembly**
*For any* scene plan where all scenes have complete media assets (visual, audio, captions), the Assembler should produce a draft video file.
**Validates: Requirements 6.1**

**Property 19: Scene sequence preservation**
*For any* assembled video, the scenes should appear in the same order as specified in the ScenePlan, preserving the sequence_number ordering.
**Validates: Requirements 6.2**

**Property 20: Draft video persistence**
*For any* successfully assembled draft video, it should be stored at a retrievable path for critique.
**Validates: Requirements 6.5**

**Property 21: Incomplete asset detection**
*For any* scene plan with missing media assets, the assembly process should fail and report which specific scenes lack which asset types.
**Validates: Requirements 6.6**

### Critique Properties

**Property 22: Multi-dimensional quality evaluation**
*For any* draft video, the Critic should generate a QualityReport containing scores for all dimensions: semantic_alignment, pacing, visual_quality, and scene_cohesion, each in the range [0, 1].
**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

**Property 23: Scene-specific feedback generation**
*For any* quality evaluation where one or more dimension scores fall below the threshold, the Critic should generate specific feedback identifying which scenes require improvement.
**Validates: Requirements 7.7**

**Property 24: Refinement flagging**
*For any* quality evaluation where the overall score falls below the configured threshold, the video should be flagged for refinement.
**Validates: Requirements 7.8**

### Refinement Properties

**Property 25: Feedback analysis and scene identification**
*For any* quality report flagging scenes for improvement, the Replanner should analyze the feedback and identify specific scenes requiring regeneration.
**Validates: Requirements 8.1, 8.2**

**Property 26: Refined prompt generation**
*For any* scene identified for regeneration, the Replanner should create a refined prompt that incorporates the critique feedback.
**Validates: Requirements 8.3**

**Property 27: Selective regeneration**
*For any* refinement plan with identified scenes, the Executor should regenerate only the flagged scenes, leaving other scenes unchanged.
**Validates: Requirements 8.4**

**Property 28: Iterative refinement loop**
*For any* video with quality scores below threshold and remaining iterations, the system should execute the refinement cycle: reassemble → critique → replan → regenerate.
**Validates: Requirements 8.5, 8.6**

**Property 29: Quality threshold exit condition**
*For any* video where quality scores exceed the configured threshold, the system should finalize the video and exit the refinement loop regardless of remaining iterations.
**Validates: Requirements 8.7**

**Property 30: Maximum iteration exit condition**
*For any* video that reaches the maximum refinement iteration count, the system should finalize the video with the best available version even if quality scores remain below threshold.
**Validates: Requirements 8.8**

### Orchestration Properties

**Property 31: Agent execution sequence**
*For any* video processing job, agents should execute in the correct sequence: Planner → Executor → Assembler → Critic, and if refinement is needed: Replanner → Executor → Assembler → Critic (loop).
**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

**Property 32: Structured agent communication**
*For any* message passed between agents, it should conform to the defined data model schemas (ScenePlan, MediaAsset, QualityReport, RefinementPlan).
**Validates: Requirements 9.6**

**Property 33: Error logging and graceful degradation**
*For any* agent failure, the system should log detailed error information and attempt graceful degradation (e.g., using partial results, fallback services).
**Validates: Requirements 9.7, 12.1**

### External Service Integration Properties

**Property 34: API authentication**
*For any* external API call, the system should include the configured authentication credentials (API keys, tokens) in the request.
**Validates: Requirements 10.1**

**Property 35: Rate limit handling**
*For any* API response indicating rate limiting (e.g., HTTP 429), the system should apply exponential backoff before retrying.
**Validates: Requirements 10.2**

**Property 36: Retry exhaustion error reporting**
*For any* API call that fails after all retry attempts are exhausted, the system should return a descriptive error message indicating the failure reason.
**Validates: Requirements 10.4**

### Configuration Properties

**Property 37: Configuration loading**
*For any* system initialization, configuration should be loaded from the specified configuration file and validated against the schema.
**Validates: Requirements 11.1**

**Property 38: Configuration usage**
*For any* configured API endpoint or credential, the system should use that value in corresponding service calls rather than hardcoded defaults.
**Validates: Requirements 11.2, 11.3**

**Property 39: Configuration validation**
*For any* configuration missing required values or containing invalid values, the system should return descriptive error messages identifying the specific configuration issues.
**Validates: Requirements 11.4**

**Property 40: Configuration hot-reload**
*For any* configuration change while the system is running, the system should reload the configuration and apply changes without requiring restart.
**Validates: Requirements 11.7**

### Error Handling Properties

**Property 41: Alternative approach fallback**
*For any* media generation error, the system should attempt alternative approaches (e.g., different API, simplified prompt, cached assets) before failing completely.
**Validates: Requirements 12.2**

**Property 42: User-friendly error messages**
*For any* unrecoverable error, the system should return an error message that is understandable to non-technical users, avoiding technical jargon and stack traces.
**Validates: Requirements 12.3**

**Property 43: Partial work preservation**
*For any* processing job that fails partway through, the system should preserve all successfully generated media assets for potential reuse.
**Validates: Requirements 12.4**

**Property 44: Network resilience**
*For any* operation that fails due to network connectivity loss, the system should queue the operation for automatic retry when connectivity is restored.
**Validates: Requirements 12.5**

**Property 45: Service fallback**
*For any* external service that becomes unavailable, the system should attempt to use configured fallback services where available.
**Validates: Requirements 12.6**

### Performance Properties

**Property 46: Pipeline isolation**
*For any* two videos being processed concurrently, their processing pipelines should be isolated such that assets, state, and errors from one do not affect the other.
**Validates: Requirements 13.1**

**Property 47: Resource cleanup**
*For any* completed video processing job, all associated resources (temporary files, memory buffers, API connections) should be released.
**Validates: Requirements 13.5**

### Output Format Properties

**Property 48: Video format compliance**
*For any* finalized video, it should be in MP4 format with H.264 codec, matching the configured resolution and frame rate.
**Validates: Requirements 14.1, 14.2, 14.3, 14.4**

**Property 49: Soft subtitle embedding**
*For any* video with captions, the captions should be embedded as soft subtitles (not burned-in), allowing them to be toggled on/off.
**Validates: Requirements 14.5**

**Property 50: Metadata generation**
*For any* finalized video, the system should generate a metadata file containing scene information, quality scores, iteration count, and processing timestamps.
**Validates: Requirements 14.6**

### Monitoring Properties

**Property 51: Metrics tracking**
*For any* video processing job when monitoring is enabled, the system should track and store quality scores, refinement cycle count, processing time per stage, and API success/failure rates.
**Validates: Requirements 15.1, 15.2, 15.3, 15.4**

**Property 52: Quality degradation alerting**
*For any* video where quality metrics fall below configured alert thresholds, the system should generate an alert for administrator review.
**Validates: Requirements 15.6**

## Error Handling

### Error Categories

**Input Validation Errors:**
- Missing required text content
- Unsupported file formats
- Invalid file references (non-existent files)
- Malformed configuration

**External Service Errors:**
- API authentication failures
- API rate limiting
- API service unavailability
- Malformed API responses
- Network connectivity issues

**Processing Errors:**
- Media generation failures
- Video assembly failures
- Insufficient system resources
- Corrupted media files

**Agent Errors:**
- LLM API failures
- Invalid agent outputs (schema violations)
- Agent timeout

### Error Handling Strategies

**Retry with Exponential Backoff:**
- Applied to: API calls, network operations
- Configuration: max_retries (default: 3), initial_delay (default: 1s), backoff_multiplier (default: 2)
- Implementation: Use tenacity library or custom retry decorator

**Fallback Services:**
- Video Generation: If Veo fails, try Runway; if both fail, use placeholder images
- TTS: If AWS Polly fails, try HuggingFace; if both fail, use silent video with captions only
- Transcription: If AWS Transcribe fails, skip transcription and use user-provided text

**Graceful Degradation:**
- If critique fails: Skip refinement, return draft video with warning
- If caption generation fails: Return video without captions
- If specific scene fails: Mark scene as failed, continue with other scenes

**Error Propagation:**
- Unrecoverable errors: Propagate to orchestrator, return error to user
- Recoverable errors: Log, attempt recovery, continue processing
- Partial failures: Complete what's possible, return partial results with error details

**Error Logging:**
- All errors logged with: timestamp, component, error type, error message, stack trace, context (video_id, scene_id)
- Log levels: DEBUG (retry attempts), INFO (fallback usage), WARNING (degraded functionality), ERROR (failures), CRITICAL (system failures)

### Error Response Format

```python
class ErrorResponse:
    error_code: str  # e.g., "INPUT_VALIDATION_ERROR", "API_FAILURE"
    message: str  # User-friendly message
    details: Optional[Dict[str, Any]]  # Technical details for debugging
    recoverable: bool  # Whether user can retry
    suggestions: Optional[List[str]]  # Suggested actions for user
```

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary values, special characters)
- Error conditions (API failures, invalid inputs, missing configuration)
- Integration points between components
- Mock external services to test error handling

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must be preserved (e.g., scene order, data persistence)
- Round-trip properties (e.g., serialize/deserialize, store/retrieve)
- Metamorphic properties (e.g., adding scenes increases duration)

Both approaches are complementary: unit tests catch concrete bugs and validate specific scenarios, while property tests verify general correctness across a wide input space.

### Property-Based Testing Configuration

**Framework:** Use Hypothesis (Python) for property-based testing

**Configuration:**
- Minimum 100 iterations per property test (due to randomization)
- Each test tagged with: **Feature: ai-video-orchestration-engine, Property {number}: {property_text}**
- Each correctness property implemented by a SINGLE property-based test
- Use custom strategies for domain objects (InputContent, Scene, ScenePlan, etc.)

**Example Test Structure:**
```python
from hypothesis import given, strategies as st
import pytest

@given(st.text(min_size=1))
def test_property_1_text_input_acceptance(text_input):
    """
    Feature: ai-video-orchestration-engine
    Property 1: Text input acceptance
    For any non-empty text string, the system should accept and parse it successfully.
    """
    input_content = InputContent(text=text_input)
    result = system.process_input(input_content)
    assert result.is_valid()
    assert result.text == text_input
```

### Unit Testing Strategy

**Test Organization:**
- Tests organized by component (test_planner.py, test_executor.py, test_critic.py, etc.)
- Use pytest framework with fixtures for common setup
- Mock external services using unittest.mock or pytest-mock

**Coverage Areas:**

*Input Processing:*
- Valid inputs with various text lengths and media combinations
- Invalid inputs (missing text, unsupported formats)
- Edge cases (very long text, special characters, Unicode)

*Planning:*
- Single scene vs. multi-scene content
- Different content types (blog, script, product description)
- Edge cases (very short content, very long content)

*Execution:*
- Successful media generation
- API failures and retries
- User-provided media handling
- Parallel scene processing

*Assembly:*
- Complete asset sets
- Missing assets
- Scene ordering
- Transition application

*Critique:*
- Various quality levels
- Edge cases (perfect video, very poor video)
- Feedback generation

*Refinement:*
- Single scene regeneration
- Multiple scene regeneration
- Iteration limits

*Orchestration:*
- Full pipeline execution
- Error handling at each stage
- Iteration loop behavior

**Integration Tests:**
- End-to-end pipeline with mocked external services
- Agent communication and data flow
- Error propagation through pipeline
- Configuration loading and usage

### Test Data Strategy

**Synthetic Data Generation:**
- Use Hypothesis strategies for property tests
- Create fixtures for common test scenarios
- Generate realistic scene plans, media assets, quality reports

**Mock External Services:**
- Create mock adapters for video generation, TTS, transcription
- Simulate various response scenarios (success, failure, rate limiting)
- Use recorded responses for realistic testing

**Test Isolation:**
- Each test should be independent
- Use temporary directories for file operations
- Clean up resources after each test

### Continuous Testing

**Pre-commit Hooks:**
- Run unit tests on changed files
- Run linting and type checking

**CI/CD Pipeline:**
- Run full unit test suite
- Run property-based tests with 100+ iterations
- Generate coverage reports (target: 80%+ coverage)
- Run integration tests with mocked services

**Performance Testing:**
- Benchmark key operations (scene generation, video assembly)
- Monitor memory usage during processing
- Test concurrent video processing

## Implementation Notes

### Phase 1: MVP (Core Pipeline)

**Scope:**
- Input processing and validation
- Planner agent with basic scene breakdown
- Executor agent with video generation and TTS
- Basic video assembly (no transitions)
- Single iteration (no critique/refinement)

**External Services:**
- One video generation API (Veo or Runway)
- One TTS service (AWS Polly)
- FFmpeg for video assembly

**Deliverable:** System that takes text input and produces a basic video with visuals and audio

### Phase 2: Iterative Refinement

**Scope:**
- Critic agent with LLM-based quality evaluation
- Replanner agent for feedback analysis
- Refinement loop with configurable iterations
- Selective scene regeneration
- Quality threshold configuration

**Enhancements:**
- Improved scene transitions
- Caption generation and embedding
- Better error handling and fallbacks

**Deliverable:** System that iteratively improves video quality through automated critique

### Phase 3: Advanced Features (Stretch Goals)

**Scope:**
- Automatic thumbnail generation
- Emotion-based background music selection
- Quality metrics dashboard
- Multi-language support with Indic voices
- User-provided video integration
- Advanced scene transitions and effects

**Enhancements:**
- Performance optimization (caching, parallel processing)
- Monitoring and observability
- A/B testing for different generation strategies

### Technology Choices Rationale

**Python:** Rich ecosystem for AI/ML, excellent LLM libraries, good video processing tools

**LangChain/LlamaIndex:** Simplifies LLM agent orchestration, provides structured output parsing

**FFmpeg:** Industry-standard video processing, supports all required formats and operations

**AWS Services:** Reliable, scalable, good documentation, Indic language support

**Hypothesis:** Mature property-based testing framework, good integration with pytest

### Key Design Decisions

**Multi-Agent Architecture:** Separates concerns, allows independent testing and improvement of each agent

**Iterative Refinement:** Differentiates from simple automation, provides quality guarantees

**Adapter Pattern for External Services:** Enables easy swapping of services, simplifies testing with mocks

**Structured Data Models:** Ensures type safety, enables validation, simplifies serialization

**Configuration-Driven:** Allows deployment flexibility without code changes

**Graceful Degradation:** Prioritizes delivering something useful over failing completely

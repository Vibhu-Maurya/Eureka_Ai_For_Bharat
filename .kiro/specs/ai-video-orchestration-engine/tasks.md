# Implementation Plan: OrchestRAI Video Engine

## Overview

This implementation plan breaks down the OrchestRAI Video Engine into discrete, incremental coding tasks. The system will be built using Python for Lambda functions, AWS CDK for infrastructure, and FFmpeg for video processing. Each task builds on previous work, with property-based tests integrated throughout to validate correctness early.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Create Python project with virtual environment
  - Set up AWS CDK project structure
  - Configure S3 buckets (uploads, transcripts, audio, drafts, finals, temp)
  - Configure DynamoDB tables (ContentMetadata, WorkflowState, ScriptVersions, Translations, ScenePlans, QualityEvaluations, FinalVideos)
  - Set up CloudWatch log groups and metric namespaces
  - Create shared Python utilities module for AWS service clients
  - _Requirements: 1.1, 1.2, 1.6, 1.7, 2.2, 3.7, 4.6, 5.4, 8.7, 11.1, 11.3, 12.1, 12.2_

- [ ] 2. Implement API Gateway and Upload Handler Lambda
  - [x] 2.1 Create API Gateway REST API with three endpoints
    - Define POST /api/v1/upload endpoint
    - Define GET /api/v1/status/{workflowId} endpoint
    - Define GET /api/v1/video/{videoId} endpoint
    - Configure API key authentication
    - Configure rate limiting (100 requests/minute per key)
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.6_
  
  - [x] 2.2 Implement Upload Handler Lambda function
    - Validate file format (MP4, MOV, AVI) and duration (5-30 minutes)
    - Validate text article inputs
    - Generate unique content ID using UUID
    - Upload content to S3 with appropriate prefix
    - Create ContentMetadata record in DynamoDB
    - Initiate Step Functions workflow
    - Return workflow ID and status
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 2.3 Write property test for duration validation
    - **Property 1: Duration Validation**
    - **Validates: Requirements 1.3**
  
  - [ ]* 2.4 Write property test for format validation
    - **Property 2: Format Validation**
    - **Validates: Requirements 1.4**
  
  - [ ]* 2.5 Write property test for error message completeness
    - **Property 3: Error Message Completeness**
    - **Validates: Requirements 1.5**
  
  - [ ]* 2.6 Write property test for content ID uniqueness
    - **Property 4: Content ID Uniqueness**
    - **Validates: Requirements 1.6**
  
  - [ ]* 2.7 Write property test for metadata persistence
    - **Property 5: Metadata Persistence Completeness**
    - **Validates: Requirements 1.7**
  
  - [ ]* 2.8 Write unit tests for upload handler edge cases
    - Test file too large (>500MB)
    - Test missing required fields
    - Test S3 upload failure handling
    - _Requirements: 1.5_

- [ ] 3. Implement Transcript Extractor Lambda
  - [x] 3.1 Create Transcript Extractor Lambda function
    - Detect content type (video vs text)
    - For video: initiate Amazon Transcribe job with language detection
    - Poll for transcription completion
    - Parse transcription JSON and extract segments with timestamps
    - Store transcript in S3
    - For text: pass through directly
    - Update WorkflowState in DynamoDB
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6_
  
  - [x] 3.2 Implement error handling and retry logic
    - Handle Transcribe service failures
    - Implement exponential backoff retry (3 attempts)
    - Log errors to CloudWatch with context
    - Send user notification on failure
    - _Requirements: 2.4, 3.6_
  
  - [ ]* 3.3 Write property test for transcript storage
    - **Property 6: Transcript Storage Consistency**
    - **Validates: Requirements 2.2**
  
  - [ ]* 3.4 Write property test for multi-language support
    - **Property 7: Multi-Language Support**
    - **Validates: Requirements 2.3**
  
  - [ ]* 3.5 Write property test for timestamp preservation
    - **Property 9: Timestamp Preservation**
    - **Validates: Requirements 2.5**
  
  - [ ]* 3.6 Write unit tests for transcript extractor
    - Test video transcription flow
    - Test text passthrough flow
    - Test Transcribe job failure
    - _Requirements: 2.1, 2.6_

- [x] 4. Checkpoint - Verify upload and transcription flow
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Script Generator Lambda
  - [x] 5.1 Create Script Generator Lambda function
    - Load transcript from S3
    - Construct Bedrock prompt for script generation
    - Call Amazon Bedrock with Claude model
    - Parse response to extract hook, scenes, and CTA
    - Validate script structure (hook + scenes + CTA)
    - Validate total duration (30-90 seconds)
    - Store script in ScriptVersions table with version number
    - Handle iteration feedback if present
    - _Requirements: 3.1, 3.2, 3.3, 3.7_
  
  - [x] 5.2 Implement retry logic and error handling
    - Retry Bedrock API calls up to 3 times
    - Handle throttling with exponential backoff
    - Log errors to CloudWatch
    - _Requirements: 3.6_
  
  - [ ]* 5.3 Write property test for script structure completeness
    - **Property 10: Script Structure Completeness**
    - **Validates: Requirements 3.2**
  
  - [ ]* 5.4 Write property test for script duration constraints
    - **Property 11: Script Duration Constraints**
    - **Validates: Requirements 3.3**
  
  - [ ]* 5.5 Write property test for version tracking
    - **Property 13: Version Tracking**
    - **Validates: Requirements 3.7**
  
  - [ ]* 5.6 Write unit tests for script generator
    - Test hook generation
    - Test scene extraction
    - Test CTA generation
    - Test feedback incorporation
    - _Requirements: 3.2_

- [-] 6. Implement Translation Service Lambda
  - [x] 6.1 Create Translation Service Lambda function
    - Load script from DynamoDB
    - For each target language, construct Bedrock translation prompt
    - Call Amazon Bedrock for translation
    - Validate translation output
    - Detect cultural flags (if any)
    - Store translations in Translations table with language tags
    - _Requirements: 4.1, 4.2, 4.4, 4.6_
  
  - [ ]* 6.2 Write property test for translation completeness
    - **Property 14: Translation Completeness**
    - **Validates: Requirements 4.1, 4.6**
  
  - [ ]* 6.3 Write property test for multi-language support (translation)
    - **Property 7: Multi-Language Support** (translation component)
    - **Validates: Requirements 4.2**
  
  - [ ]* 6.4 Write unit tests for translation service
    - Test translation for specific language pair
    - Test cultural flag detection
    - Test error handling for unsupported language
    - _Requirements: 4.1, 4.4_

- [ ] 7. Implement Scene Planner Lambda
  - [x] 7.1 Create Scene Planner Lambda function
    - Load script from DynamoDB
    - Construct Bedrock prompt for scene planning
    - Call Amazon Bedrock to generate visual descriptions
    - Extract timestamp ranges from source video
    - Assign asset types (video_clip, text_overlay, image)
    - Assign transitions (cut, fade, dissolve)
    - Store scene plan in ScenePlans table with sequence numbers
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 7.2 Implement error handling with simplified retry
    - Handle Bedrock failures
    - Retry with simplified parameters if needed
    - Log errors to CloudWatch
    - _Requirements: 5.5_
  
  - [ ]* 7.3 Write property test for scene plan completeness
    - **Property 15: Scene Plan Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [ ]* 7.4 Write property test for scene sequence ordering
    - **Property 16: Scene Sequence Ordering**
    - **Validates: Requirements 5.4**
  
  - [ ]* 7.5 Write unit tests for scene planner
    - Test visual description generation
    - Test timestamp extraction
    - Test asset type assignment
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 8. Checkpoint - Verify script generation pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement Voice Synthesizer Lambda
  - [x] 9.1 Create Voice Synthesizer Lambda function
    - Load translations from DynamoDB
    - For each language, select appropriate Polly neural voice
    - Call Amazon Polly to synthesize speech
    - Configure output format (MP3, 48kHz)
    - Store audio files in S3 with language-specific naming
    - Validate audio duration matches scene plan timing (±2 seconds)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6_
  
  - [ ] 9.2 Implement retry logic for Polly failures
    - Retry synthesis up to 3 times
    - Log errors to CloudWatch
    - _Requirements: 6.5_
  
  - [ ]* 9.3 Write property test for audio format compliance
    - **Property 17: Audio Format Compliance**
    - **Validates: Requirements 6.3, 6.4**
  
  - [ ]* 9.4 Write property test for audio-scene duration synchronization
    - **Property 18: Audio-Scene Duration Synchronization**
    - **Validates: Requirements 6.6**
  
  - [ ]* 9.5 Write property test for multi-language support (voice)
    - **Property 7: Multi-Language Support** (voice component)
    - **Validates: Requirements 6.2**
  
  - [ ]* 9.6 Write unit tests for voice synthesizer
    - Test audio generation for specific language
    - Test Polly error handling
    - Test audio format validation
    - _Requirements: 6.1, 6.3_

- [-] 10. Implement Video Assembler Lambda and EC2 setup
  - [ ]* 10.1 Set up EC2 instance with FFmpeg
    - Create EC2 instance with Amazon Linux 2
    - Install FFmpeg with required codecs
    - Configure security groups for Lambda access
    - Set up S3 access for video processing
    - _Requirements: 7.1_
    - _Note: Using Lambda with FFmpeg layer instead of EC2 for MVP_
  
  - [x] 10.2 Create Video Assembler Lambda function
    - Load scene plan and audio file references
    - Download source video from S3
    - For each scene, extract video segment using FFmpeg
    - Convert segments to 9:16 aspect ratio with padding/crop
    - Overlay audio narration on video
    - Generate SRT subtitle file from script
    - Burn subtitles onto video (24pt, white with black outline)
    - Apply transitions between scenes
    - Concatenate all segments into final draft
    - Encode output as MP4 with H.264
    - Upload draft video to S3
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  
  - [ ] 10.3 Implement FFmpeg error handling
    - Handle FFmpeg processing errors
    - Log detailed error information to CloudWatch
    - Clean up temporary files
    - _Requirements: 7.8_
  
  - [ ]* 10.4 Write property test for video aspect ratio compliance
    - **Property 19: Video Aspect Ratio Compliance**
    - **Validates: Requirements 7.2**
  
  - [ ]* 10.5 Write property test for audio track presence
    - **Property 20: Audio Track Presence**
    - **Validates: Requirements 7.3**
  
  - [ ]* 10.6 Write property test for subtitle presence and styling
    - **Property 21: Subtitle Presence and Styling**
    - **Validates: Requirements 7.4**
  
  - [ ]* 10.7 Write property test for video format compliance
    - **Property 23: Video Format Compliance**
    - **Validates: Requirements 7.6**
  
  - [ ]* 10.8 Write property test for draft video storage uniqueness
    - **Property 24: Draft Video Storage Uniqueness**
    - **Validates: Requirements 7.7**
  
  - [ ]* 10.9 Write unit tests for video assembler
    - Test segment extraction
    - Test aspect ratio conversion
    - Test audio overlay
    - Test subtitle burning
    - Test FFmpeg error handling
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 11. Checkpoint - Verify video assembly pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement AI Critic Lambda
  - [ ] 12.1 Create AI Critic Lambda function
    - Load draft video metadata and original transcript
    - Construct Bedrock evaluation prompt
    - Call Amazon Bedrock to evaluate video quality
    - Parse evaluation response to extract scores
    - Validate all scores are between 0-100
    - Calculate weighted overall score (semantic 40%, pacing 25%, readability 20%, cultural 15%)
    - Extract feedback (strengths, weaknesses, suggestions, critical issues)
    - Store evaluation in QualityEvaluations table
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_
  
  - [ ] 12.2 Implement error handling for evaluation failures
    - Handle Bedrock API failures
    - Assign default failing score (0) on error
    - Log errors to CloudWatch
    - _Requirements: 8.8_
  
  - [ ]* 12.3 Write property test for quality score range validity
    - **Property 26: Quality Score Range Validity**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.5**
  
  - [ ]* 12.4 Write property test for weighted average calculation
    - **Property 27: Weighted Average Calculation**
    - **Validates: Requirements 8.6**
  
  - [ ]* 12.5 Write property test for evaluation storage
    - **Property 28: Evaluation Storage**
    - **Validates: Requirements 8.7**
  
  - [ ]* 12.6 Write unit tests for AI critic
    - Test score calculation for each dimension
    - Test weighted average computation
    - Test feedback generation
    - Test error handling
    - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 13. Implement Step Functions workflow orchestration
  - [ ] 13.1 Create Step Functions state machine definition
    - Define ExtractTranscript state with Lambda integration
    - Define GenerateScript state with Lambda integration
    - Define TranslateScript state with Lambda integration
    - Define PlanScenes state with Lambda integration
    - Define SynthesizeVoice state with Lambda integration
    - Define AssembleVideo state with Lambda integration
    - Define EvaluateQuality state with Lambda integration
    - Define CheckQualityThreshold choice state
    - Define IncrementIteration state for refinement loop
    - Define FlagForReview state for max iterations
    - Define FinalizeOutput state for completion
    - Configure retry policies (3 attempts, exponential backoff)
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ] 13.2 Implement workflow state tracking
    - Update WorkflowState in DynamoDB at each stage transition
    - Log stage transitions to CloudWatch
    - Track stage durations as CloudWatch metrics
    - _Requirements: 10.5, 10.6, 12.2_
  
  - [ ] 13.3 Implement refinement loop logic
    - Compare quality score to threshold
    - Increment iteration count
    - Pass critic feedback to script generator
    - Enforce maximum 3 iterations
    - Flag for manual review if threshold not met
    - Mark as final if threshold met
    - Store iteration history in DynamoDB
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_
  
  - [ ]* 13.4 Write property test for refinement trigger logic
    - **Property 29: Refinement Trigger Logic**
    - **Validates: Requirements 9.1, 9.4, 9.5**
  
  - [ ]* 13.5 Write property test for feedback propagation
    - **Property 30: Feedback Propagation**
    - **Validates: Requirements 9.2**
  
  - [ ]* 13.6 Write property test for iteration limit enforcement
    - **Property 31: Iteration Limit Enforcement**
    - **Validates: Requirements 9.3**
  
  - [ ]* 13.7 Write property test for pipeline stage ordering
    - **Property 33: Pipeline Stage Ordering**
    - **Validates: Requirements 10.2**
  
  - [ ]* 13.8 Write property test for retry mechanism consistency
    - **Property 12: Retry Mechanism Consistency**
    - **Validates: Requirements 3.6, 6.5, 10.3**
  
  - [ ]* 13.9 Write unit tests for workflow orchestration
    - Test stage sequence execution
    - Test retry logic with exponential backoff
    - Test refinement loop decision making
    - Test max iteration handling
    - _Requirements: 10.2, 10.3, 9.1, 9.3_

- [ ] 14. Implement Completion Handler Lambda
  - [x] 14.1 Create Completion Handler Lambda function
    - Load final video from S3
    - Generate presigned URL with 7-day expiration
    - Generate presigned URL for subtitle file
    - Update FinalVideos table with complete metadata
    - Send notification to user with video URL
    - Update workflow status to "completed"
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 10.7_
  
  - [ ] 14.2 Implement artifact retention policy
    - Tag intermediate artifacts with 30-day retention
    - Configure S3 lifecycle policy for cleanup
    - _Requirements: 11.6_
  
  - [ ]* 14.3 Write property test for presigned URL generation
    - **Property 39: Presigned URL Generation**
    - **Validates: Requirements 11.2**
  
  - [ ]* 14.4 Write property test for final metadata completeness
    - **Property 40: Final Metadata Completeness**
    - **Validates: Requirements 11.3**
  
  - [ ]* 14.5 Write property test for subtitle file availability
    - **Property 41: Subtitle File Availability**
    - **Validates: Requirements 11.4**
  
  - [ ]* 14.6 Write unit tests for completion handler
    - Test presigned URL generation
    - Test metadata storage
    - Test notification sending
    - _Requirements: 11.2, 11.3, 11.5_

- [ ] 15. Checkpoint - Verify complete workflow
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement Status and Video Retrieval endpoints
  - [x] 16.1 Create Status Handler Lambda function
    - Query WorkflowState table by workflowId
    - Return current stage, progress, and status
    - Return quality score if completed
    - Return error message if failed
    - Handle workflow not found (404)
    - _Requirements: 13.2_
  
  - [x] 16.2 Create Video Retrieval Handler Lambda function
    - Query FinalVideos table by videoId and language
    - Generate presigned URLs for video and subtitles
    - Return video metadata
    - Handle video not found (404)
    - _Requirements: 13.3_
  
  - [ ]* 16.3 Write unit tests for status and retrieval handlers
    - Test status retrieval for various workflow states
    - Test video retrieval with language parameter
    - Test 404 handling
    - _Requirements: 13.2, 13.3_

- [ ] 17. Implement monitoring and observability
  - [ ] 17.1 Implement comprehensive CloudWatch logging
    - Log all API requests and responses with correlation IDs
    - Log all stage transitions with timestamps
    - Log all errors with stack traces and context
    - Ensure correlation IDs propagate through all services
    - _Requirements: 12.1, 12.3, 12.7_
  
  - [ ] 17.2 Implement CloudWatch metrics
    - Track generation time for each pipeline stage
    - Track cost metrics for Bedrock, Polly, Transcribe
    - Track total videos generated
    - Track average quality scores
    - Track average processing times
    - _Requirements: 12.2, 12.5, 12.6_
  
  - [ ] 17.3 Configure CloudWatch alarms
    - Create alarm for failure rate exceeding 5%
    - Create alarm for processing time exceeding thresholds
    - Create alarm for cost exceeding budget
    - _Requirements: 12.4_
  
  - [ ]* 17.4 Write property test for API request logging
    - **Property 43: API Request Logging**
    - **Validates: Requirements 12.1**
  
  - [ ]* 17.5 Write property test for error logging completeness
    - **Property 25: Error Logging Completeness**
    - **Validates: Requirements 2.4, 7.8, 12.3**
  
  - [ ]* 17.6 Write property test for correlation ID presence
    - **Property 47: Correlation ID Presence**
    - **Validates: Requirements 12.7**
  
  - [ ]* 17.7 Write unit tests for monitoring
    - Test log entry creation
    - Test metric recording
    - Test alarm triggering
    - _Requirements: 12.1, 12.2, 12.4_

- [ ] 18. Implement API authentication and rate limiting
  - [ ] 18.1 Configure API Gateway authentication
    - Set up API key requirement for all endpoints
    - Configure usage plans
    - Implement 401 error for missing/invalid API keys
    - _Requirements: 13.4_
  
  - [ ] 18.2 Implement rate limiting
    - Configure 100 requests per minute per API key
    - Return 429 error when limit exceeded
    - _Requirements: 13.6_
  
  - [ ] 18.3 Implement input validation
    - Validate all request payloads
    - Return 400 errors for invalid inputs with descriptive messages
    - Validate HTTP status codes for all operations
    - _Requirements: 13.5, 13.7, 13.8_
  
  - [ ]* 18.4 Write property test for authentication enforcement
    - **Property 48: Authentication Enforcement**
    - **Validates: Requirements 13.4**
  
  - [ ]* 18.5 Write property test for input validation
    - **Property 49: Input Validation**
    - **Validates: Requirements 13.5**
  
  - [ ]* 18.6 Write property test for rate limiting
    - **Property 50: Rate Limiting**
    - **Validates: Requirements 13.6**
  
  - [ ]* 18.7 Write property test for HTTP status code correctness
    - **Property 51: HTTP Status Code Correctness**
    - **Validates: Requirements 13.7**
  
  - [ ]* 18.8 Write property test for error response format
    - **Property 52: Error Response Format**
    - **Validates: Requirements 13.8**
  
  - [ ]* 18.9 Write unit tests for API security
    - Test API key validation
    - Test rate limiting behavior
    - Test input validation errors
    - _Requirements: 13.4, 13.5, 13.6_

- [ ] 19. Implement integration tests
  - [ ]* 19.1 Write integration test for upload to transcription flow
    - Test end-to-end: upload → S3 → Transcribe → transcript storage
    - _Requirements: 1.1, 2.1, 2.2_
  
  - [ ]* 19.2 Write integration test for script generation to translation flow
    - Test: generate script → translate to multiple languages → store all versions
    - _Requirements: 3.1, 4.1, 4.6_
  
  - [ ]* 19.3 Write integration test for scene planning to video assembly flow
    - Test: plan scenes → synthesize voice → assemble video
    - _Requirements: 5.1, 6.1, 7.1_
  
  - [ ]* 19.4 Write integration test for evaluation to refinement flow
    - Test: evaluate video → trigger refinement → regenerate
    - _Requirements: 8.1, 9.1, 9.2_
  
  - [ ]* 19.5 Write integration test for complete pipeline
    - Test: upload → process → evaluate → deliver
    - _Requirements: 10.1, 10.2, 10.7_

- [ ] 20. Final checkpoint - End-to-end validation
  - Run all unit tests and property tests
  - Run all integration tests
  - Verify complete workflow with sample video
  - Verify multi-language generation
  - Verify refinement loop behavior
  - Ensure all CloudWatch logs and metrics are working
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions
- Use Hypothesis library for property-based testing in Python
- Use LocalStack for local AWS service testing during development
- All Lambda functions should use Python 3.11 runtime
- Use AWS CDK for infrastructure as code
- FFmpeg processing runs on EC2 for better performance and control

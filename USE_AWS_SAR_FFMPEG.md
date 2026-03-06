# Solution: Use AWS Serverless Application Repository FFmpeg Layer

## The Problem

The FFmpeg static build from johnvansickle.com is missing the `drawtext` filter, which is needed for text overlays. The error shows:

```
[AVFilterGraph @ 0x20b91bc0] No such filter: 'drawtext'
```

## Solution Options

### Option 1: Use AWS SAR FFmpeg Layer (Recommended)

AWS Serverless Application Repository has pre-built FFmpeg layers with all filters enabled.

#### Steps:

1. **Go to AWS Console** → Lambda → Layers
2. **Browse AWS Serverless Application Repository**
3. **Search for**: "ffmpeg lambda layer"
4. **Deploy** one of these popular layers:
   - `serverlesspub/ffmpeg-lambda-layer`
   - `ffmpeg-lambda-layer` by various publishers

5. **Get the Layer ARN** from the deployed application
6. **Attach to Lambda**:
```bash
C:\Python313\python.exe -m awscli lambda update-function-configuration ^
    --function-name OrchestRAIComputeStack-VideoAssembler2FE6ABF1-dCrVWB22taM7 ^
    --layers [NEW_LAYER_ARN] ^
    --region us-east-1
```

### Option 2: Build FFmpeg with Drawtext Support

This requires Docker and is more complex:

1. Use Docker to build FFmpeg with `--enable-libfreetype --enable-fontconfig`
2. Create layer ZIP with proper structure
3. Upload to Lambda

### Option 3: Simplify Video Generation (Quick Fix)

Modify the Lambda code to create videos without text overlays:
- Use solid color backgrounds
- Add text as subtitles only (not burned in)
- Use simpler video generation

## Recommended Action

**Use Option 1** - AWS SAR has battle-tested FFmpeg layers with all filters enabled.

### Quick Steps:

1. Open AWS Console: https://console.aws.amazon.com/lambda
2. Go to Layers → Browse AWS Serverless Application Repository
3. Search "ffmpeg"
4. Deploy the layer
5. Copy the Layer ARN
6. Run: `.\add_custom_ffmpeg_layer.bat [NEW_ARN]`

## Why This Happened

The johnvansickle.com static builds are minimal and don't include all filters. The `drawtext` filter requires:
- libfreetype (font rendering)
- libfontconfig (font configuration)

These weren't compiled into the static build we downloaded.

## Current Status

✅ FFmpeg is now accessible at `/opt/bin/ffmpeg`  
✅ FFmpeg runs successfully  
❌ FFmpeg missing `drawtext` filter  
❌ Cannot create text overlays  

## Next Steps

1. Use AWS SAR to get a full-featured FFmpeg layer
2. OR: Modify code to work without text overlays
3. OR: Build custom FFmpeg with all filters

The fastest solution is AWS SAR - it's pre-built, tested, and includes all filters.

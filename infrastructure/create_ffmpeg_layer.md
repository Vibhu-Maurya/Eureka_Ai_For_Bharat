# FFmpeg Lambda Layer Setup

The Video Assembler Lambda requires FFmpeg to process videos. Since FFmpeg is not available by default in Lambda, we need to add it as a Lambda Layer.

## Option 1: Use Pre-built FFmpeg Layer (Recommended)

Use a pre-built FFmpeg layer from the Serverless Application Repository:

1. Go to AWS Lambda Console → Layers
2. Click "Create layer"
3. Or use this public layer ARN for us-east-1:
   ```
   arn:aws:lambda:us-east-1:145266761615:layer:ffmpeg:4
   ```

## Option 2: Build Your Own Layer

If you need a custom FFmpeg build:

### Prerequisites
- Docker installed on your machine
- AWS CLI configured

### Build Steps

1. Create a directory for the layer:
```bash
mkdir -p ffmpeg-layer/bin
cd ffmpeg-layer
```

2. Download FFmpeg static build:
```bash
# For Linux x86_64 (Lambda runtime)
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg-release-amd64-static.tar.xz
cp ffmpeg-*-amd64-static/ffmpeg bin/
cp ffmpeg-*-amd64-static/ffprobe bin/
chmod +x bin/ffmpeg bin/ffprobe
```

3. Create the layer structure:
```bash
mkdir -p opt/bin
mv bin/* opt/bin/
```

4. Create the layer ZIP:
```bash
zip -r ffmpeg-layer.zip opt/
```

5. Upload to AWS Lambda:
```bash
aws lambda publish-layer-version \
    --layer-name ffmpeg \
    --description "FFmpeg and FFprobe for video processing" \
    --zip-file fileb://ffmpeg-layer.zip \
    --compatible-runtimes python3.11 \
    --region us-east-1
```

6. Note the Layer ARN from the output and add it to your Lambda function.

## Adding Layer to Lambda Function

### Via AWS Console
1. Go to Lambda Console → Functions → VideoAssembler
2. Scroll to "Layers" section
3. Click "Add a layer"
4. Select "Specify an ARN"
5. Enter the FFmpeg layer ARN
6. Click "Add"

### Via CDK (Update compute_stack.py)

Add this after creating the video_assembler function:

```python
# Add FFmpeg layer
ffmpeg_layer_arn = "arn:aws:lambda:us-east-1:145266761615:layer:ffmpeg:4"
ffmpeg_layer = lambda_.LayerVersion.from_layer_version_arn(
    self, "FFmpegLayer",
    ffmpeg_layer_arn
)
self.video_assembler.add_layers(ffmpeg_layer)
```

## Verification

Test that FFmpeg is available in your Lambda:

```python
import subprocess
result = subprocess.run(['/opt/bin/ffmpeg', '-version'], capture_output=True, text=True)
print(result.stdout)
```

## Alternative: Use AWS Elemental MediaConvert

For production workloads, consider using AWS Elemental MediaConvert instead of FFmpeg in Lambda:
- Better performance for video processing
- No Lambda timeout concerns
- Professional-grade video encoding
- Pay per minute of video processed

This would require updating the Video Assembler to submit MediaConvert jobs instead of processing directly.

import React, { useState, useRef, useEffect } from 'react';
import {
  Camera,
  Upload,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Sparkles,
  ShieldCheck,
  Eye,
  SunMedium,
  User,
  Scan
} from 'lucide-react';
import Button from '../common/Button';

export default function FaceCameraCapture({ onVerifyFace, currentStatus, isSubmitting }) {
  const [mode, setMode] = useState('camera'); // 'camera' | 'upload'
  const [streamActive, setStreamActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [capturedBlob, setCapturedBlob] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  // Initialize camera stream
  useEffect(() => {
    let stream = null;

    async function startCamera() {
      if (mode !== 'camera' || capturedImage) return;
      try {
        setCameraError(null);
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setStreamActive(true);
        }
      } catch (err) {
        setCameraError('Camera access unavailable or permission denied. You may switch to Upload Photo.');
        setStreamActive(false);
      }
    }

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [mode, capturedImage]);

  // Capture frame from video
  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    // Mirror the capture for natural preview
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob);
        setCapturedImage(url);
        setCapturedBlob(blob);
      }
    }, 'image/jpeg', 0.95);
  };

  // Handle uploaded face photo
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setCapturedImage(url);
      setCapturedBlob(file);
    }
  };

  const handleRetake = () => {
    if (capturedImage) URL.revokeObjectURL(capturedImage);
    setCapturedImage(null);
    setCapturedBlob(null);
  };

  const triggerVerification = () => {
    if (capturedBlob && onVerifyFace) {
      onVerifyFace(capturedBlob);
    }
  };

  return (
    <div className="face-verification-layout">
      {/* Hidden canvas for snapshot capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Viewfinder Area */}
      <div className="face-viewfinder-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Scan size={18} style={{ color: '#38bdf8' }} />
            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Biometric Viewfinder</span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className={`scenario-pill-btn ${mode === 'camera' ? 'active' : ''}`}
              onClick={() => {
                setMode('camera');
                handleRetake();
              }}
            >
              <Camera size={13} style={{ display: 'inline', marginRight: '4px' }} />
              Use Camera
            </button>
            <button
              type="button"
              className={`scenario-pill-btn ${mode === 'upload' ? 'active' : ''}`}
              onClick={() => {
                setMode('upload');
                handleRetake();
              }}
            >
              <Upload size={13} style={{ display: 'inline', marginRight: '4px' }} />
              Upload Photo
            </button>
          </div>
        </div>

        {/* Viewport Frame */}
        <div className="viewfinder-camera-area">
          {capturedImage ? (
            <img
              src={capturedImage}
              alt="Captured Subject"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : mode === 'camera' ? (
            cameraError ? (
              <div style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                <Camera size={44} style={{ margin: '0 auto 12px', color: '#64748b' }} />
                <p style={{ fontSize: '0.88rem', color: '#e2e8f0', marginBottom: '8px' }}>Camera Inactive</p>
                <p style={{ fontSize: '0.78rem', maxWidth: '320px', margin: '0 auto 16px' }}>{cameraError}</p>
                <Button size="sm" variant="outline" onClick={() => setMode('upload')}>
                  Switch to Photo Upload
                </Button>
              </div>
            ) : (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="camera-stream-video"
              />
            )
          ) : (
            <div style={{ textAlign: 'center', padding: '24px' }}>
              <Upload size={44} style={{ margin: '0 auto 12px', color: '#38bdf8' }} />
              <p style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', marginBottom: '6px' }}>
                Upload Live Subject Photo
              </p>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '16px' }}>
                Select a front-facing headshot (JPEG / PNG)
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
              />
              <Button
                variant="primary"
                size="sm"
                icon={Upload}
                onClick={() => fileInputRef.current?.click()}
              >
                Browse Image
              </Button>
            </div>
          )}

          {/* Biometric Overlay Guide */}
          {!capturedImage && (
            <div className="face-oval-guide">
              <div className="face-corner-mark corner-tl" />
              <div className="face-corner-mark corner-tr" />
              <div className="face-corner-mark corner-bl" />
              <div className="face-corner-mark corner-br" />
            </div>
          )}
        </div>

        {/* Viewfinder Controls */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '14px' }}>
          <div>
            {capturedImage ? (
              <Button variant="secondary" size="sm" icon={RefreshCw} onClick={handleRetake}>
                Retake Photo
              </Button>
            ) : mode === 'camera' && streamActive ? (
              <Button variant="accent" icon={Camera} onClick={handleCapture}>
                Capture Frame
              </Button>
            ) : null}
          </div>

          <div>
            {capturedImage && (
              <Button
                variant="primary"
                icon={Sparkles}
                loading={isSubmitting || currentStatus === 'processing'}
                onClick={triggerVerification}
              >
                Verify Biometric Match
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Biometric Guidelines Card */}
      <div className="face-instructions-card">
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-brand-navy)' }}>
            Biometric Standards
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Strict standards for 1:1 facial embedding cross-matching
          </p>
        </div>

        <div className="instruction-list">
          <div className="instruction-item">
            <span className="instruction-num">01</span>
            <div>
              <strong style={{ color: 'var(--text-primary)', display: 'block', fontSize: '0.85rem' }}>
                Face Directly Forward
              </strong>
              <span>Position head directly perpendicular to camera without tilt or yaw.</span>
            </div>
          </div>

          <div className="instruction-item">
            <span className="instruction-num">02</span>
            <div>
              <strong style={{ color: 'var(--text-primary)', display: 'block', fontSize: '0.85rem' }}>
                Balanced Illumination
              </strong>
              <span>Ensure even ambient lighting with zero strong shadows or backlighting glare.</span>
            </div>
          </div>

          <div className="instruction-item">
            <span className="instruction-num">03</span>
            <div>
              <strong style={{ color: 'var(--text-primary)', display: 'block', fontSize: '0.85rem' }}>
                Remove Obstructions
              </strong>
              <span>Remove sunglasses, face masks, or hats that occlude eyes, nose, or chin.</span>
            </div>
          </div>

          <div className="instruction-item">
            <span className="instruction-num">04</span>
            <div>
              <strong style={{ color: 'var(--text-primary)', display: 'block', fontSize: '0.85rem' }}>
                Align Inside Oval
              </strong>
              <span>Ensure face completely occupies the blue designated biometric guide.</span>
            </div>
          </div>
        </div>

        <div
          style={{
            padding: '12px 14px',
            backgroundColor: '#eff6ff',
            borderRadius: 'var(--radius-md)',
            border: '1px solid #bfdbfe',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.8rem',
            color: '#1e40af',
          }}
        >
          <ShieldCheck size={18} style={{ flexShrink: 0 }} />
          <span>Compliant with ICAO Doc 9303 Part 9 Biometrics Standard</span>
        </div>
      </div>
    </div>
  );
}

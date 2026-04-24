import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";

interface PickupQrScannerProps {
  open: boolean;
  busy?: boolean;
  onClose: () => void;
  onDetected: (value: string) => Promise<void> | void;
}

export function PickupQrScanner({ busy = false, onClose, onDetected, open }: PickupQrScannerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const frameRef = useRef<number | null>(null);
  const detectorRef = useRef<BarcodeDetector | null>(null);
  const handledRef = useRef(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState("Point QR X at the camera to confirm exam-paper pickup.");

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    handledRef.current = false;
    setError(null);
    setStatus("Requesting camera access...");

    const stopScanner = () => {
      if (frameRef.current !== null) {
        window.cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
      detectorRef.current = null;
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };

    const scanFrame = () => {
      if (!open || handledRef.current || !videoRef.current || !detectorRef.current) {
        return;
      }

      detectorRef.current
        .detect(videoRef.current)
        .then((barcodes) => {
          const value = barcodes.find((item) => item.rawValue?.trim())?.rawValue?.trim();
          if (value && !handledRef.current) {
            handledRef.current = true;
            setStatus("QR detected. Confirming pickup...");
            void Promise.resolve(onDetected(value)).catch(() => {
              handledRef.current = false;
            });
            return;
          }
          frameRef.current = window.requestAnimationFrame(scanFrame);
        })
        .catch(() => {
          frameRef.current = window.requestAnimationFrame(scanFrame);
        });
    };

    const startScanner = async () => {
      if (!window.BarcodeDetector) {
        setError("This browser does not support camera QR scanning yet. Please use Chrome or Edge on a camera-enabled device.");
        setStatus("Camera-only scanning is required.");
        return;
      }

      try {
        detectorRef.current = new window.BarcodeDetector({ formats: ["qr_code"] });
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            facingMode: { ideal: "environment" },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        setStatus("Camera ready. Scan the printed QR X only.");
        frameRef.current = window.requestAnimationFrame(scanFrame);
      } catch (err) {
        const nextMessage =
          err instanceof DOMException && err.name === "NotAllowedError"
            ? "Camera permission was denied. Please allow camera access to scan the printed QR."
            : "Unable to start the camera scanner right now.";
        setError(nextMessage);
        setStatus("Camera-only scanning is required.");
      }
    };

    void startScanner();
    return stopScanner;
  }, [onDetected, open]);

  return (
    <Modal
      open={open}
      title="Scan QR X"
      onClose={() => {
        if (!busy) {
          onClose();
        }
      }}
      footer={
        <div className="pickup-scanner__footer">
          <span>{status}</span>
          <Button type="button" variant="outline" onClick={onClose} disabled={busy}>
            Close
          </Button>
        </div>
      }
    >
      <div className="pickup-scanner">
        <div className="pickup-scanner__preview">
          <video ref={videoRef} autoPlay muted playsInline />
          <div className="pickup-scanner__frame" aria-hidden="true" />
        </div>
        <p className="pickup-scanner__hint">Camera only. Image upload and photo-library scanning are disabled.</p>
        {error ? <p className="pickup-scanner__error">{error}</p> : null}
      </div>
    </Modal>
  );
}

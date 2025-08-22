# Demo Plan (<=10 minutes)

1. Quick intro (30s): Problem statement: detect 'reel' vs 'non-reel' traffic on-device using metadata.
2. Architecture (1m): show pipeline diagram: Capture -> Windowing -> Features -> TFLite model -> On-device inference.
3. Data (1m): mention synthetic data and plan for real captures via VPNService.
4. Model (1m): show accuracy and confusion matrix (from notebook).
5. Live demo (3m): Launch app, start capture, play reels and show live predictions.
6. Metrics & limitations (1m): latency, model size, privacy (metadata-only).
7. Closing (30s): next steps and improvements.

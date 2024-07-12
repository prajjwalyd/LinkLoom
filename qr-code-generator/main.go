package main

import (
    _ "encoding/base64"
    "github.com/skip2/go-qrcode"
    "net/http"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func generateQRCode(w http.ResponseWriter, r *http.Request) {
    url := r.URL.Query().Get("url")
    if url == "" {
        http.Error(w, "Missing URL parameter", http.StatusBadRequest)
        return
    }
    png, err := qrcode.Encode(url, qrcode.Medium, 256)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    w.Header().Set("Content-Type", "image/png")
    w.Write(png)
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.HandleFunc("/generate_qr", generateQRCode)
    http.ListenAndServe("0.0.0.0:5002", nil)
}

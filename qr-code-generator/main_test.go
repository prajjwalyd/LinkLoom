package main

import (
    "net/http"
    "net/http/httptest"
    "testing"
)

func TestGenerateQRCode(t *testing.T) {
    req, err := http.NewRequest("GET", "/generate_qr?url=http://example.com", nil)
    if err != nil {
        t.Fatal(err)
    }

    rr := httptest.NewRecorder()
    handler := http.HandlerFunc(generateQRCode)
    handler.ServeHTTP(rr, req)

    if status := rr.Code; status != http.StatusOK {
        t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
    }

    if ct := rr.Header().Get("Content-Type"); ct != "image/png" {
        t.Errorf("handler returned wrong content type: got %v want %v", ct, "image/png")
    }
}

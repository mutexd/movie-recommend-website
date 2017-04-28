package main

import (
    "log"
    "net/http"
    "io/ioutil"
)

func main() {
    /* Register callback to URI */
    http.Handle("/movielist/ranked", http.HandlerFunc(simple))

    /* Start the backend server */
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatal("ListenAndServe:", err)
    }
}

func simple(w http.ResponseWriter, req *http.Request) {
    /* Setting header to support CORS */
    if origin := req.Header.Get("Origin"); origin != "" {
        w.Header().Set("Access-Control-Allow-Origin", origin)
        w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
    }
    w.Header().Set("Content-Type", "application/json")

    /* Preflight options request */
    if req.Method == "OPTIONS" {
        return
    }

    /* Read JSON file into memory */
    dat, err := ioutil.ReadFile("movies.json")
    if err != nil {
        log.Fatal(err)
    }

    _, err = w.Write(dat)
    if err != nil {
        log.Fatal(err)
    }
}


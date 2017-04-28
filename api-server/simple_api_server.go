package main

import (
    "log"
    "net/http"
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
    "encoding/json"
)

var db *sql.DB      /*< Gloabal database pointer */

func main() {
    var err error

    /* Initialize DB instance */
    db, err = sql.Open("mysql", "webmovie:cf_webmovie@tcp(127.0.0.1:3306)/webmovie")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    /* Register callback to URI */
    http.Handle("/movielist/ranked", http.HandlerFunc(simple))

    /* Start the backend server */
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatal("ListenAndServe:", err)
    }
}

type rankedList struct {
    Title string    `json:"title"`
    Year int        `json:"year"`
    Duration string `json:"duration"`
    Thumb string    `json:"thumb"`
    ImdbUrl string  `json:"imdbUrl"`
    Rating int32    `json:"rating"`
}

func simple(w http.ResponseWriter, req *http.Request) {
    var (
        name string
        imdb_url string
        thumb string
        duration string
        info rankedList
    )
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

    rows, err := db.Query("select ReadableTitle, imdb_url, Poster, Runtime from movieItem where id < 30")
    if err != nil {
	    log.Fatal(err)
    }
    defer rows.Close()

    /* Prepare JSON response */
    enc := json.NewEncoder(w)
    fmt.Fprintf(w, "[")
    jsonBeginFlag := true
    for rows.Next() {
        if jsonBeginFlag == true {
            jsonBeginFlag = false
        } else {
            fmt.Fprintf(w, ",")
        }
	    err := rows.Scan(&name, &imdb_url, &thumb, &duration)
	    if err != nil {
		    log.Fatal(err)
	    }
        info.Title = name
        info.Duration = duration
        info.Thumb = thumb
        info.Rating = 0
        info.ImdbUrl = imdb_url
        if err = enc.Encode(info); err != nil {
            log.Println(err)
        }
    }
    fmt.Fprintf(w, "]")

    /* Always check error */
    if err := rows.Err(); err != nil {
	    log.Fatal(err)
    }

}


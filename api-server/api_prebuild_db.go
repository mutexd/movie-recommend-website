package main

import (
    "log"
    "fmt"
    "net/http"
    "net/url"
    "time"
    "strings"
    "database/sql"
    "encoding/json"
    _ "github.com/go-sql-driver/mysql"
)

/* Global instances */
var db *sql.DB
var myClient = &http.Client{Timeout: 10 * time.Second}

type omdbResponse struct {
    ReadableTitle string    `json:"Title"`      // Readable title
    Poster string   `json:"Poster"`
    Runtime string  `json:"Runtime"`
    ImdbID string   `json:"imdbID"`
    Response string `json:"Response"`
    Error string    `json:"Error"`
}

func main() {
    var (
        name string
        id int
        err error
        omdbRes omdbResponse
    )

    /* Initialize DB instance */
    db, err := sql.Open("mysql", "webmovie:cf_webmovie@tcp(127.0.0.1:3306)/webmovie")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    /* We should make sure DB connection works fine here */
    if err = db.Ping(); err != nil {
        log.Fatal(err)
    }

    /* Add columns Poster|Runtime|ImdbID into table */
    stmt, err := db.Prepare("alter table movieItem "+
        "add column `Poster` VARCHAR(300) NOT NULL after `imdb_url`," +
        "add column `Runtime` CHAR(10) NOT NULL after `Poster`,"+
        "add column `ImdbID` CHAR(20) NOT NULL after `Runtime`," +
        "add column `ReadableTitle` VARCHAR(100) NOT NULL after `ImdbID`")
    if err != nil {
        log.Println(err)
    }
    if _, err := stmt.Exec(); err != nil {
        log.Println(err)
    }

    /* Query all movies in DB */
    rows, err := db.Query("select id, title from movieItem where id<300")
    if err != nil {
	    log.Fatal(err)
    }
    defer rows.Close()

    /* Query omdbapi for each movie */
    for rows.Next() {
	    if err := rows.Scan(&id, &name); err != nil {
		    log.Println(err)
	    }
        queryName := prepareUrl(name[:len(name)-7])
        err = getJson("http://www.omdbapi.com/?" + queryName, &omdbRes)
        if err != nil {
            log.Println(err)
            log.Println(id)
            omdbRes.Poster = "oops.jpeg"
            omdbRes.Runtime = "0 min"
            omdbRes.ImdbID = "unknown"
            omdbRes.ReadableTitle = "unknown"
        } else if strings.Compare(omdbRes.Response,"False") == 0 {
            log.Println(id, queryName, omdbRes.Error)
            omdbRes.Poster = "oops.jpeg"
            omdbRes.Runtime = "0 min"
            omdbRes.ImdbID = "unknown"
            omdbRes.ReadableTitle = name
        }
        /* Update information into DB */
        stmt, err := db.Prepare("update movieItem set Poster=\""+omdbRes.Poster+
            "\", Runtime=\""+omdbRes.Runtime+
            "\", ImdbID=\"" +omdbRes.ImdbID +
            "\", ReadableTitle=\""  +omdbRes.ReadableTitle  +"\" where id="+fmt.Sprintf("%d",id))
        if err != nil {
            log.Println(err)
        }
        if _, err := stmt.Exec(); err != nil {
            log.Println(err)
        }
    }

    /* Always check error */
    if err := rows.Err(); err != nil {
	    log.Fatal(err)
    }
}



/*
 *  The title from MovieLens are weird
 *  -> "The Sum of Us" will be "Sum of Us, The"
 *  -> "Life of Brian" will be "Monty Python's Life of Brian"
 *  -> "Star Trek: The Wrath of Khan"
 *  We need to convert it to readable and searchable one
 */
func removeParentheses(s string) string {
    if i := strings.Index(s, "("); i<0 {
        return s
    } else {
        return s[:i-1]
    }
}
func removeComma(s string) string {
    if i := strings.Index(s, ","); i<0 {
        return s
    } else {
        return s[:i]
    }
}
func checkQuota(s string) string {
    if i := strings.Index(s, "'s"); i<0 || i+2 >= len(s){
        return s
    } else {
        return s[i+2:]
    }
}

func checkColon(s string) string {
    if i := strings.Index(s, ":"); i<0{
        return s
    } else {
        return s[i+1:]
    }
}

func prepareUrl(rawUrl string) string {
    s1 := removeComma(removeParentheses(rawUrl))
    s2 := checkColon(checkQuota(s1))
    parameters := url.Values{}
    parameters.Add("t", s2)
    ret := parameters.Encode()
    return ret
}

func getJson(url string, target interface{}) error {
    r, err := myClient.Get(url)
    if err != nil {
        return err
    }
    defer r.Body.Close()

    return json.NewDecoder(r.Body).Decode(target)
}

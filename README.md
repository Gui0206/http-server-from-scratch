# 🚀 Build Your Own HTTP Server

[![CodeCrafters](https://img.shields.io/badge/CodeCrafters-Challenge-blue)](https://app.codecrafters.io/courses/http-server/overview)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://www.python.org/)

This repository contains my Python implementation for the **"Build Your Own HTTP server"** challenge by [CodeCrafters](https://codecrafters.io). 

The goal of this project was to understand how the web actually works under the hood by building a functional HTTP server from scratch, without relying on external web frameworks like Flask or Django. I manipulated raw TCP sockets, handled byte streams, and manually parsed HTTP protocols.

## ✨ Features

* **Concurrent Connections:** Handles multiple clients simultaneously using Python's `threading`.
* **HTTP Parsing:** Manually extracts Methods, Paths, Headers, and Bodies from raw byte streams.
* **GZIP Compression:** Reads the `Accept-Encoding` header and compresses responses on the fly.
* **File Operations:** Serves files from the disk (`GET`) and saves uploaded files (`POST`).


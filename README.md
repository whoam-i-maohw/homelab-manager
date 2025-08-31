# homelab-manager

Homelab Manager project to manage different things on my homelab server(s) 😊

# Perquisites

- Python3.11+ and that can be downloaded from here [https://www.python.org/downloads/]
- Make build tool and that can be downloaded from here [https://www.gnu.org/software/make/]
- Poetry package manager for python and that can be downloaded from here [https://python-poetry.org/]

# How to know what can be done for the project

```bash
make
```

# How to setup the project's components

```bash
make setup
```

# How to run tests for the project's components

```bash
make test-coverage
```

# Project's Features

- [ ] Video
  - [x] Video Downloader
    - [x] YouTube Video
      - [x] Download a YouTube video to a specific directory
      - [x] Download a YouTube video to a directory of the video's channel name inside a base-directory
      - [x] Download YouTube videos from a urls txt file to a specific directory
  - [ ] Video's Metadata Persistence
    - [x] YouTube Video Metadata Persistence
  - [ ] Video Tags Generation
  - [ ] Video Transcribe Generation
- [ ] Audio
  - [ ] Audio Downloader
  - [ ] Audio's Metadata Persistence
  - [ ] Audio Tags Generation
  - [ ] Audio Transcribe Generation

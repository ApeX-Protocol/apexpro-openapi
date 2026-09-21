# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.2] - 2026-09-21

### Removed

- Dropped two v3 endpoints that were not meant to be part of the public
  client surface. Callers on 3.2.0-3.4.1 that used them should move to the
  internal service that owns those endpoints.

## [3.2.0] - 2026-03-16

### Added

- Internal maintenance release.

## [1.0.0] - 2022-06-03

### Added

- The `apexpro` module.
- MANIFEST, README, LICENSE, and CHANGELOG files.

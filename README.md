# Best New Music Digest

[![Latest Release](https://img.shields.io/github/release/vanillaSlice/best-new-music-digest.svg)](https://github.com/vanillaSlice/best-new-music-digest/releases/latest)
[![Build Status](https://img.shields.io/travis/com/vanillaSlice/best-new-music-digest/master.svg)](https://travis-ci.com/vanillaSlice/best-new-music-digest)
[![Coverage Status](https://img.shields.io/coveralls/github/vanillaSlice/best-new-music-digest/master.svg)](https://coveralls.io/github/vanillaSlice/best-new-music-digest?branch=master)
[![License](https://img.shields.io/github/license/vanillaSlice/best-new-music-digest.svg)](LICENSE)

Scrapes new music info and emails out a digest.

## Configuration

The following properties can be configured:

| Name                     | Purpose                                                                                 |
| ------------------------ | --------------------------------------------------------------------------------------- |
| `ALWAYS_EMAIL`           | If an email should always be sent out even if there are no updates (defaults to false). |
| `DAD_JOKE`               | Include a dad joke in the email (defaults to true).                                     |
| `DAY_OF_WEEK_TO_RUN`     | Day of week that the application should be run (defaults to monday).                    |
| `MONGODB_URI`            | URI to MongoDB.                                                                         |
| `PITCHFORK_ALBUMS`       | Include Pitchfork albums in digest (defaults to true).                                  |
| `PITCHFORK_TRACKS`       | Include Pitchfork tracks in digest (defaults to true).                                  |
| `RECIPIENT_EMAIL`        | Email address to send digests to.                                                       |
| `SENDER_EMAIL`           | Email address of the digest sender.                                                     |
| `SENDER_NAME`            | Name of the digest sender.                                                              |
| `SENDGRID_API_KEY`       | SendGrid API key required to send emails.                                               |
| `SENDGRID_TEMPLATE_ID`   | SendGrid template ID required to send emails.                                           |
| `SPUTNIKMUSIC_ALBUMS`    | Include Sputnikmusic albums in digest (defaults to true).                               |
| `THE_NEEDLE_DROP_ALBUMS` | Include The Needle Drop albums in digest (defaults to true).                            |
| `THE_NEEDLE_DROP_TRACKS` | Include The Needle Drop tracks in digest (defaults to true).                            |
| `YOUTUBE_API_KEY`        | YouTube API key (optional if YouTube reliant scrapers are switched off).                |

Create a `.env` file using the `.env-starter` as a guide.

## Running

From your terminal/command prompt run:

```
./run.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

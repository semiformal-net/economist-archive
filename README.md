# economist archive

Archive issues of the economist audio edition.

This will help you download and index back issues of the audio edition of the economist. It is meant to run once and download all the issues in one go. It saves the issues as zip files and prepares a sqlite database containing issue information.

The process is in two parts: zip files, database.

## 1 zip files

Recommended workflow:

```
python econscrape.py | tee /tmp/econscrape
egrep '^OK' /tmp/econscrape | awk '{print $2}' | xargs -n1 -P6 -- curl -s -O

[ -w "Issue_9136_20190330_The_Economist_Full_Edition.zip" ] && mv "Issue_9136_20190330_The_Economist_Full_Edition.zip" "Issue_9136_20190330_The_Economist_Full_edition.zip"
[ -w "Issue_9230_20210123_The_Economist_Full_edition.zip" ] && mv "Issue_9230_20210123_The_Economist_Full_edition.zip" "Issue_9229_20210123_The_Economist_Full_edition.zip"
[ -w "Issue_8902_20140830_The_Economist_Full_edition.zip" ] && zip -d Issue_8902_20140830_The_Economist_Full_edition.zip "__MACOSX/*"
[ -w "Issue_9166_20191026_The_Economist_Full_edition.zip" ] && zip -d Issue_9166_20191026_The_Economist_Full_edition.zip "__MACOSX/*"
[ -w "Issue_9365_20230930_The_Economist_Full_edition.zip" ] && zip -d Issue_9365_20230930_The_Economist_Full_edition.zip "__MACOSX/*"
```

`econscrape.py` is the program that supports this part of the process. It will find valid issues within a given date range spit out urls to download from. The workflow above gathers the urls to a file, then uses xargs & curl to download the files in batch before finally patching a few bugs (see below).

You may edit the date range in `ecoscrape.py` to collect more or fewer issues, but the archives don't extend back forever (try 2014 or 2015).

### 1.1 Bugs

Gathering a decade of weekly issues there are bound to be a few inconsistencies. The workflow above patches all the bugs that I have found:

1. Issue 9136 `404`

You may see `Error: fetching http://audiocdn.economist.com/sites/default/files/AudioArchive/2019/20190330/Issue_9136_20190330_The_Economist_Full_edition.zip: HTTP Error 404: Not Found`. This file is legitimately missing from the economist server. The file has a capital E so `http://audiocdn.economist.com/sites/default/files/AudioArchive/2019/20190330/Issue_9136_20190330_The_Economist_Full_Edition.zip` works instead.

2. No issue the week of 20230805

You may see `Error: fetching http://audiocdn.economist.com/sites/default/files/AudioArchive/2023/20230805/Issue_9358_20230805_The_Economist_Full_edition.zip: HTTP Error 404: Not Found`. This is because there was a [summer double issue](https://myaccount.economist.com/s/article/double-issue-FAQ)

3. There are two valid urls for issue 9230 (and no 9229):

Both these urls are valid:

  - `http://audiocdn.economist.com/sites/default/files/AudioArchive/2021/20210123/Issue_9230_20210123_The_Economist_Full_edition.zip`
  - `http://audiocdn.economist.com/sites/default/files/AudioArchive/2021/20210130/Issue_9230_20210130_The_Economist_Full_edition.zip`

I suggest renaming `Issue_9230_20210123_The_Economist_Full_edition.zip` to `Issue_9229_20210123_The_Economist_Full_edition.zip`

4. there are a few zip files with a `__MACOSX/` directory that contains cruft. The directory may be safely removed.

The issues with `__MACOSX` dir:

  - `Issue_8902_20140830_The_Economist_Full_edition.zip`
  - `Issue_9166_20191026_The_Economist_Full_edition.zip`
  - `Issue_9365_20230930_The_Economist_Full_edition.zip`

## 2 Database

The second part is to build a sqlite database of all the contents of the issues. This is optional.

The program processes the zip files and stores:

  - id3 tag information
  - file information
  - cover art

This is controlled with `ecofiledb.py`. The end of that file contains some configuration. Point it to the directory where you saved the issue zip file (above) and configure the location of the DB and of the covers. Then execute the program.

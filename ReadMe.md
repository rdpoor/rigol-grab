# rigol_grab
_Capture Rigol DS1054Z Oscilloscope Display as a .png file, for MacOS,
Linux and Windows_

The Rigol DS1054Z Oscilloscope is a powerful multi-channel tool for the
hobbyist and professional alike.  It includes a USB port, but there's not
much in the way of software support for Linux and macOS systems.

rigol_grab is a cross-platform Python-based script that lets you capture the
contents of the Rigol Oscilloscope display to a .png file, such as this:

![Rigol Screen Capture](/rigol.png)

## Setup

The setup process assumes you already have `git`, `Python` and `pipenv` set up
on your machine.  In a shell window:

    > cd <your chosen directory>
    > git clone ...
    > pipenv install

## Running rigol_grab

In a shell window:

    > cd <your chosen directory>
    > pipenv shell
    > python rigol_grab.py

## Options

`rigol_grab.py` accepts command line arguments:

    --verbose print additional information
    --filename specify the pathname of the saved .png file
    --auto_open: automatically open the .png using your system viewer

 ## Caveats

 There are a few known bugs.  Top scientists are investigating these issues and
 hope to have a fix.  Or you can propose a fix with a pull request:

 * The program always throws an error upon exiting.  This appears to be benign.
 * Once every two or three times, the .png data is corrupted.  If this happens,
 just re-run the script.
 * There's been zero testing on Linux or Windows systems.  But it might work.

 ## Support

Feel free to post issues and feature requests in the [Issues section](https://github.com/rdpoor/rigol-grab/issues).

And if the spirit so moves you, please submit pull requests for enhancements.

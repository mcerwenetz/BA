package com.example.sensortryout;

import java.util.Locale;

public class Util {

    // fmt with default locale, 1..4 arguments should suffice
    public static String fmt(String formatString, Object arg1) {
        return String.format(Locale.getDefault(), formatString,
                arg1);
    }

    public static String fmt(String formatString, Object arg1, Object arg2) {
        return String.format(Locale.getDefault(), formatString,
                arg1, arg2);
    }

    public static String fmt(String formatString, Object arg1, Object arg2,
                             Object arg3) {
        return String.format(Locale.getDefault(), formatString,
                arg1, arg2, arg3);
    }

    public static String fmt(String formatString, Object arg1, Object arg2,
                             Object arg3, Object arg4) {
        return String.format(Locale.getDefault(), formatString,
                arg1, arg2, arg3, arg4);
    }

}

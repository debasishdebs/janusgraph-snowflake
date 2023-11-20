package com.sstech.graphdb.extractor.utils;

import java.util.Locale;

public final class OSUtils {
    private static String OS = null;
    public static String getOsName()
    {
        if(OS == null) {
//            OS = System.getProperty("os.name");
            OS = System.getProperty("os.name", "generic").toLowerCase(Locale.ENGLISH);
        }
        return OS;
    }
    public static boolean isWindows()
    {
        return getOsName().contains("win");
    }

    public static boolean isUnix() {
        return getOsName().contains("nux");
    } // and so on

    public static boolean isMac() {
        return getOsName().contains("mac") || getOsName().contains("darwin");
    }
}

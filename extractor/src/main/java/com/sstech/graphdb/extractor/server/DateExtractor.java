package com.sstech.graphdb.extractor.server;

import java.text.SimpleDateFormat;
import java.util.Calendar;

import net.snowflake.client.jdbc.internal.joda.time.DateTime;

public class DateExtractor {

	public static void main(String[] args) {
		DateTime dt1 = new DateTime("2013-12-29T22:59:21.969z");
		String date = "2013-12-30T22:59:21.969z";
	    DateTime dt2 = new DateTime("2013-12-30T22:59:21.969z");
	 //   SimpleDateFormat dt1 = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ");
	    System.out.println(dt1.getDayOfMonth() +" "+dt1.getYear() +" "+dt1.getMonthOfYear() +" "+dt1.getHourOfDay() + " "+dt1.getMinuteOfHour() + " "+dt1.getSecondOfMinute());
	    
	    Calendar c = Calendar.getInstance();
	   // c.setTime(dt2);
	    

	}
}

from filter import csv_filter as csfl

csv_filter = csfl("Colombia")
csv_filter.save_excel()

csv_filter = csfl("Argetina")
csv_filter.save_excel()

csv_filter = csfl("Brazil")
csv_filter.save_excel()

import pdfplumber

import sys
sys.path.append('c:/Users/shenjinyun/Desktop/python_work/TICS')
import snap
import merge
import intersection
import cell
import table

file_name = input("请输入PDF文档名称：\n")

with pdfplumber.open(file_name) as pdf:
	page_num = len(pdf.pages)
	total_tables = []
	
	for i in range(0, page_num):
		p = pdf.pages[i]
		
		raw_edges = p.edges
		
		snapped_edges = snap.snap_edges(raw_edges)
		
		merged_edges = merge.merge_edges(snapped_edges)
		
		intersections = intersection.edges_to_intersections(merged_edges)
		
		cells = cell.intersections_to_cells(intersections)
		
		page_tables = table.cells_to_tables(p, cells)
		
		page_table_num = len(page_tables)
		for j in range(0, page_table_num):
			total_tables.append(page_tables[j])
	
	if len(total_tables):
		print("共检测到" + str(len(total_tables)) + "个表格：")
		table.show_tables(total_tables)
		
		save = input("\n是否保存表格？(y/n)\n")
	
		if save == "y":
			table.save_tables(total_tables, file_name)
	
	else:
		print("未检测到表格！")
		
	







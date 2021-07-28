import xml.etree.ElementTree as et
import chardet
import pandas as pd
import os


# we want to ignore these characters that come before the tags 
BAD_PREPEND_CHARS = {" ", "-"}


class DataFinder:

	def __init__(self, xml_files):
		self.xml_files = xml_files


		for fileid, file in enumerate(xml_files):
			self.xml_cleanup(file, fileid)
			col1, col2 = self.find_n_recoverytests_tabledata(fileid)
			self.export_to_excel(col1, col2, fileid)
			os.remove(f"temp{fileid}.xml")
			print(f"Datasets processed: {fileid+1}/{len(self.xml_files)}")

	@staticmethod
	def xml_cleanup(fp, fileid):
		"""
			- removes prepending bad chars such as spaces and dashes
			- removes special chars not fit for ASCII encoding
		"""

		# read in xml file 

		with open(fp, encoding="ISO-8859-1") as f:
			# i detected the encoding using this loc 
			# print(chardet.detect(f.read()))

			with open(f"temp{fileid}.xml", "w") as fw:

				content = f.readlines()
				for line in content:

					good_chars = []
					for char in line:
						if 0 < ord(char) <= 125:

							if char not in BAD_PREPEND_CHARS:
								good_chars.append(char)

							# ignore bad char if it prepends data we want. otherwise just write to file
							if char in BAD_PREPEND_CHARS and len(good_chars) == 0:
								continue

							fw.write(char)

						else:
							fw.write("omitted")

	@staticmethod
	def find_n_recoverytests_tabledata(fileid):

		tree = et.parse(f"temp{fileid}.xml")

		root = tree.getroot()

		n_tests_col = []
		name_col = []

		for child in root:
			child.tag == "ReportableCharts"
			for reportable_chart_data in child:

				if reportable_chart_data.tag == "XmlChart":
					for xml_chart_data in reportable_chart_data:

						name = reportable_chart_data[0].text
						
						if xml_chart_data.tag == "Bias":
							for bias_data in xml_chart_data:

								if bias_data.tag == "RecoveryData":
									for recovery_data in bias_data:
										
										if recovery_data.tag == "TotalNumberOfRecoveryTests":
											name_col.append(name)
											n_tests_col.append(recovery_data.text)			

		return name_col, n_tests_col


	def export_to_excel(self, col1, col2, fileid):
		table = pd.DataFrame({'name':col1, 'n recovery tests':col2})
		print("-->Exporting table to Excel")
		table.to_excel(f"Bias data points {fileid+1}.xlsx")


files = []

for file in os.listdir(os.getcwd()):
	filename = file.split(".")[0]
	ext = file.split(".")[1]
	if ext == "xml" and filename[:4] != "temp":
		files.append(file)


df = DataFinder(files)

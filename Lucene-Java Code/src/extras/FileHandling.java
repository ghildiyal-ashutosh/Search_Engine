package extras;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * File Handling class which runs all the file-related operations
 * @author takkyon
 *
 */
public class FileHandling {
	
	/**
	 * Get the list of files from the given folder.
	 * Returns Null is the folder does not exists.
	 * @param folderName
	 * @return
	 * @throws IOException
	 */
	public List<File> getAllFilesInFolder(String folderName) throws IOException {
		System.out.println("Reading files from " + folderName + "\n\n");
		File folder = new File(folderName);
		if (!folder.exists())
			return null;
		File[] listOfFiles = folder.listFiles();
		List<File> files = new ArrayList<>();
		for (int i = 0; i < listOfFiles.length; i++) {
		  if (listOfFiles[i].isFile()) {
		    files.add(listOfFiles[i]);
		  }
		}
		return files;
	}
	
	/**
	 * Get entire file content as a string.
	 * Each line is concatenated by a space<" ">
	 * Returns Null is file does not exists
	 * @param file
	 * @return
	 * @throws IOException
	 */
	public String getFileContent(File file) throws IOException {
		StringBuilder builder = new StringBuilder();
		if(!file.exists())
			return null;
		BufferedReader br = new BufferedReader(new FileReader(file)); 
		String line;
		while ((line = br.readLine()) != null) {
			builder.append(line.trim() + " ");
		} 
		br.close();
		return builder.toString().trim().toLowerCase();
	}
	
	/**
	 * Get the list of all the lines from the file.
	 * Returns Null is file does not exists
	 * @param file
	 * @return
	 * @throws IOException
	 */
	public List<String> getLines(File file) throws IOException {
		List<String> lines = new ArrayList<>();
		if(!file.exists())
			return null;
		BufferedReader br = new BufferedReader(new FileReader(file)); 
		String line;
		while ((line = br.readLine()) != null) {
			lines.add(line.trim().toLowerCase());
		} 
		br.close();
		return lines;
	}
	
	/**
	 * Save file with the filename and the content given
	 * @param fileName
	 * @param content
	 * @throws IOException
	 */
	public void saveFile(String fileName, String content) throws IOException{
		File file = new File(fileName);
		if(!file.exists())
			file.createNewFile();
		BufferedWriter bw = new BufferedWriter(new FileWriter(fileName));
		bw.write(content);
		bw.close();
	}
	
}

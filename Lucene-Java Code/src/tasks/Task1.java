package tasks;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.lucene.document.Document;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.TopDocs;

import extras.Constants;
import extras.FileHandling;
import extras.Indexer;
import extras.Utility;

/**
 * Run all the task1 related sub-tasks
 * @author takkyon
 *
 */
public class Task1 {

	private FileHandling fileHandling;
	private Indexer indexer;
	private Utility utility;
	private String queries[];
	private String queryFileNames[];
	private String parentFolder;
	private static Task1 instance = null;
	
	/**
	 * Create new instance of the class
	 * @return
	 * @throws IOException
	 */
	public static Task1 newInstance() throws IOException{
		if(instance == null)
			instance = new Task1();
		return instance;
	}
	
	/**
	 * Private default constructor
	 * @throws IOException
	 */
	private Task1() throws IOException{
		this.fileHandling = new FileHandling();
		this.indexer = new Indexer(Constants.INDEX_FOLDER);
		this.utility = new Utility();
		this.queries = Constants.queries;
		this.queryFileNames = Constants.queryFileNames;
		this.parentFolder = Constants.TASK_FOLDER + "/1/";
	}
	
	/**
	 * Entry point for the class, runs all the sub-tasks
	 */
	public void run() {
		try {
			// task1
			System.out.println("Indexing documents..Running Task 1(a)..\n");
			this.indexDocuments();
			this.runQueries();
		}catch(IOException ie) {
			ie.printStackTrace();
			System.err.println("IOException Found..");
		}catch(ParseException pe) {
			pe.printStackTrace();
			System.err.println("Parse Exception..");
		}
	}
	
	/**
	 * This functions runs task 2b.
	 * It runs here since we need to run task 1b,
	 * just with different Queries
	 * @param queries
	 * @param parentFolder
	 */
	public void runTask2b(String queries[], String parentFolder) {
		try {
			this.queries = queries;
			this.parentFolder = parentFolder;
			this.runQueries();
		}catch(IOException ie) {
			ie.printStackTrace();
			System.err.println("IOException Found..");
		}catch(ParseException pe) {
			pe.printStackTrace();
			System.err.println("Parse Exception..");
		}
	}
	
	/**
	 * Run searching for the queries
	 * @throws IOException
	 * @throws ParseException
	 */
	private void runQueries() throws IOException, ParseException {
		IndexSearcher searcher = this.indexer.createSearcher(Constants.INDEX_FOLDER);
		int results = 100;
		System.out.println("\n\nProcessing Queries..");
		for(int i = 0;i<this.queries.length;++i) {
			String query = this.queries[i];
			System.out.println("Searching the indexes for: " + query);
			QueryParser parser = this.indexer.createQueryParser(Constants.TAG_CONTENTS);
			TopDocs topDocs = this.indexer.getTopDocsForQuery(parser, query.toLowerCase(), results, searcher);
			List<String> documents = this.utility.getDocumentTitle(topDocs, searcher);
			this.saveDocuments(documents, this.queryFileNames[i], i + 1);
		}
	}
	
	/**
	 * Save all the documents and their score generated for the queries
	 * @param documents
	 * @param queryFileName
	 * @throws IOException
	 */
	private void saveDocuments(List<String> documents, String queryFileName, int queryId) throws IOException{
		StringBuilder builder = new StringBuilder("Query: " + queryFileName + "\n\n");
		String fileName = this.parentFolder + queryFileName.replaceAll(" ", "_");
		for(String doc: documents) {
			builder.append(queryId + "  Q0  " + doc + "  Lucene\n");
		}
		this.fileHandling.saveFile(fileName, builder.toString());
	}
	
	/**
	 * Index all the documents stored in files/corpus
	 * @throws IOException
	 */
	private void indexDocuments() throws IOException {
		List<File> files = this.fileHandling.getAllFilesInFolder(Constants.CORPUS_FOLDER);
		List<Document> documents = new ArrayList<>();
		for(File file: files) {
			String content = this.fileHandling.getFileContent(file);
			String filename = file.getName();
			System.out.println("Indexing file, " + filename);
			Document document = this.indexer.createDocument(filename, content);
			documents.add(document);
		}
		this.indexer.indexDocuments(documents);
	}
	
}

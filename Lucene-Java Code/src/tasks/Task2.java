package tasks;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.lucene.analysis.CharArraySet;
import org.apache.lucene.analysis.StopFilter;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import extras.Constants;
import extras.FileHandling;
import extras.Utility;

/**
 * Run all the task2 related sub-tasks
 * @author takkyon
 *
 */
public class Task2 {

	private FileHandling fileHandling;
	private Utility utility;
	private Task1 task1;
	private static Task2 instance = null;
	
	/**
	 * Create new instance of the class
	 * @return
	 * @throws IOException
	 */
	public static Task2 newInstance() throws IOException{
		if(instance == null)
			instance = new Task2();
		return instance;
	}
	
	/**
	 * Private default constructor
	 * @throws IOException
	 */
	private Task2() throws IOException{
		this.fileHandling = new FileHandling();
		this.utility = new Utility();
		this.task1 = Task1.newInstance();
	}
	
	/**
	 * Entry point for the class, runs all the sub-tasks
	 */
	public void run() {
		try {
			// task2
			System.out.println("Expanding Queries..Running Task 2(a)..\n");
			this.runQueryExpansion();
			
		}catch(IOException ie) {
			ie.printStackTrace();
			System.err.println("IOException Found..");
		}
	}
	
	/**
	 * Runs query expansion for n = {4 ,6, 8, 10}
	 * Two different iterations run for top 10 and top 20 documents for the query.
	 * @throws IOException
	 */
	private void runQueryExpansion() throws IOException {
		for(int n: Constants.N) {
			for(int k: Constants.K) {
				String folder = Constants.TASK_FOLDER + "/2/n" + n + "k" + k + "/";
				System.out.println("Running expansion for top " + k + " documents and adding " + n + " expansion terms..\n");
				String[] queries = this.expandQueries(n, k);
				System.out.println("Saving Expanded Queries\n");
				this.saveExpandedQueries(queries, folder);
				System.out.println("Fetching top 100 documents for new queries..");
				this.task1.runTask2b(queries, folder);
			}
		}
	}
	
	/**
	 * Expand query by adding top n to the initial query, and
	 * use only top k documents
	 * @param topTerms: n
	 * @param topDocuments: k
	 * @return
	 * @throws IOException
	 */
	private String[] expandQueries(int topTerms, int topDocuments) throws IOException {
		List<String> newQueries = new ArrayList<>();
		for(String query: Constants.queries) {
			List<File> files = this.getTopDocumentsForQuery(query, topDocuments);
			Map<String, Map<String, Set<Integer>>> invertedIndex = this.createInvertedIndex(files);
			Map<String, Double> termFreq = this.utility.sortByValue(this.getTermFreq(invertedIndex));
			List<String> topTermFreq = this.getTopTermFreq(termFreq, topTerms);
			String newQuery = this.createNewQuery(query, topTermFreq);
			newQueries.add(newQuery);
		}		
		return newQueries.toArray(new String[] {});
	}
	
	/**
	 * Save all the extended queries.
	 * Queries are found under, files/task/2/{n4n10}
	 * @param queries
	 * @param folder
	 * @throws IOException
	 */
	private void saveExpandedQueries(String[] queries, String folder) throws IOException {
		StringBuilder builder = new StringBuilder();
		for(int i = 0;i<queries.length;++i) {
			builder.append(Constants.queries[i] + "  ::  " + queries[i] + "\n\n");
		}
		this.fileHandling.saveFile(folder + "expanded_queries.txt", builder.toString());
	}
	
	/**
	 * Return top k documents for the given query
	 * @param query
	 * @param topDocuments: k
	 * @return
	 * @throws IOException
	 */
	private List<File> getTopDocumentsForQuery(String query, int topDocuments) throws IOException {
		String fileText = Constants.TASK_FOLDER + "/1/" + query.replaceAll(" ", "_");
		List<String> lines = this.fileHandling.getLines(new File(fileText));
		List<File> topDocs = new ArrayList<>();
		int i = 0;
		for(String line: lines) {
			if (i >= topDocuments)
				break;
			String temp = line.split("::")[0].trim();
			File file = new File(Constants.CORPUS_FOLDER + "/" + temp);
			if(file.exists()) {
				topDocs.add(file);
				++i;
			}
		}
		return topDocs;
	}
	
	/**
	 * Create new query by adding the list of expansion terms to the initial query
	 * @param query
	 * @param expansion
	 * @return
	 */
	private String createNewQuery(String query, List<String> expansion) {
		StringBuilder builder = new StringBuilder(query);
		for(String q: expansion) {
			builder.append(" " + q);
		}
		return builder.toString().trim();
	}
	
	/**
	 * Get top k terms to be used in expansion.
	 * Stopwords are removed from the termFreq before taking the expansion terms
	 * @param termFreq
	 * @param topTerms: k
	 * @return
	 */
	private List<String> getTopTermFreq(Map<String, Double> termFreq, int topTerms) {
		List<String> topTermFreq = new ArrayList<>();
		int i = 0;
		int k = 0;
		for(String key: termFreq.keySet()) {
			if(k < Constants.topFreqTermsToRemove) {
				++k;
			}else {
				if (i >= topTerms)
					break;
				topTermFreq.add(key);
				++i;
			}
		}
		return topTermFreq;
	}
	
	/**
	 * Get frequency for each term(across the corpus) from the inverted index
	 * @param index
	 * @return
	 */
	private Map<String, Double> getTermFreq(Map<String, Map<String, Set<Integer>>> index) {
		Map<String, Double> termFreq = new HashMap<>();
		for(String term: index.keySet()) {
			double count = 0;
			double docs = index.get(term).keySet().size() * 1.0;
			for(String doc: index.get(term).keySet())
				count += index.get(term).getOrDefault(doc, new HashSet<>()).size();
			termFreq.put(term, count);
		}
		return termFreq;
	}
	
	/**
	 * Filter stopwords using the existing stopwords list from
	 * the StandardAnalyzer class
	 * @param content
	 * @return
	 */
	private TokenStream filterStopwords(String content) {
		StandardAnalyzer analyzer = new StandardAnalyzer();
		TokenStream tokenStream = analyzer.tokenStream(Constants.TAG_CONTENTS, new StringReader(content));
		CharArraySet stopWords = analyzer.getStopwordSet();
		tokenStream = new StopFilter(tokenStream, stopWords);
		analyzer.close();
		return tokenStream;
	}
	
	/**
	 * Create Inverted index from the given list of files
	 * @param files
	 * @return
	 * @throws IOException
	 */
	private Map<String, Map<String, Set<Integer>>> createInvertedIndex(List<File> files) throws IOException {
		Map<String, Map<String, Set<Integer>>> invertedIndex = new HashMap<>();
		for(File file: files) {
			String content = this.fileHandling.getFileContent(file);
			TokenStream tokenStream = this.filterStopwords(content);
			CharTermAttribute terms = tokenStream.addAttribute(CharTermAttribute.class);
			tokenStream.reset();
			String filename = file.getName();
			int i = 0;
			while(tokenStream.incrementToken()) {
				String term = terms.toString();
				if(invertedIndex.get(term) == null)
					invertedIndex.put(term, new HashMap<>());
				
				Map<String, Set<Integer>> index = invertedIndex.get(term);
				if(index.get(filename) == null)
					index.put(filename, new HashSet<>());
				Set<Integer> positions = index.get(filename);
				positions.add(i);
				++i;
				index.put(filename,  positions);
				invertedIndex.put(term,  index);
			}
		}
		return invertedIndex;
	}
}

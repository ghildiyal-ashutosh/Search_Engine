package extras;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

public class Indexer {

	private IndexWriter indexWriter;

	public Indexer(String indexDirPath) throws IOException {
		File indexFile = new File(indexDirPath);
		if(!indexFile.exists())
			return;
		Directory indexDir = FSDirectory.open(indexFile.toPath());
		IndexWriterConfig config = new IndexWriterConfig(new StandardAnalyzer());
		this.indexWriter = new IndexWriter(indexDir, config);
	}
	
	public Document createDocument(String filename, String content) {
		Document document = new Document();
		
		// index file contents
		Field contentField = new TextField(Constants.TAG_CONTENTS, content, Field.Store.YES);
		
		// index file name
		Field fileNameField = new StringField(Constants.TAG_FILENAME, filename, Field.Store.YES);

		document.add(contentField);
		document.add(fileNameField);
		return document;
	}
	
	public void indexDocuments(List<Document> documents) throws IOException {
		this.indexWriter.deleteAll();
		this.indexWriter.addDocuments(documents);
		this.indexWriter.commit();
		this.indexWriter.close();
	}
	
	public IndexSearcher createSearcher(String indexDirPath) throws IOException {
		File indexFile = new File(indexDirPath);
		if(!indexFile.exists())
			return null;
		Directory indexDir = FSDirectory.open(indexFile.toPath());
		IndexReader reader = DirectoryReader.open(indexDir);
		return new IndexSearcher(reader);
	}
	
	public TopDocs getTopDocsForQuery(QueryParser queryParser,
			String queryText, int results, IndexSearcher searcher) throws IOException, ParseException {
		Query query = queryParser.parse(queryText);
		return searcher.search(query, results);
	}
	
	public QueryParser createQueryParser(String query) {
		return new QueryParser(query, new StandardAnalyzer());
	}

}

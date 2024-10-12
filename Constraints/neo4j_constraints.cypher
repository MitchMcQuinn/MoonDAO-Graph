// Unique constraint on Article ID
CREATE CONSTRAINT unique_article_id IF NOT EXISTS FOR (a:Article) REQUIRE a.id IS UNIQUE;

// Index on Article published date
CREATE INDEX article_published_at IF NOT EXISTS FOR (a:Article) ON (a.published_at);

// Unique constraint on Keyword word
CREATE CONSTRAINT unique_keyword_word IF NOT EXISTS FOR (k:Keyword) REQUIRE k.word IS UNIQUE;

// Index on Keyword word
CREATE INDEX keyword_word_index IF NOT EXISTS FOR (k:Keyword) ON (k.word);

// Unique constraint on Transaction txHash
CREATE CONSTRAINT unique_transaction IF NOT EXISTS FOR (t:Transaction) REQUIRE t.txHash IS UNIQUE

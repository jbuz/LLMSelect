import React, { useMemo, useState, useEffect } from 'react';
import MarkdownMessage from './MarkdownMessage';
import { chatApi } from '../services/api';

const MIN_KEYWORD_LENGTH = 4;
const WORDS_PER_MINUTE = 200;

const normalizeWord = (word) => word.toLowerCase();

const extractWords = (text) => {
  if (!text) return [];
  const matches = text.toLowerCase().match(/[a-z0-9][a-z0-9'\-]*/g);
  return matches ? matches.filter(Boolean) : [];
};

const extractSentences = (text) => {
  if (!text) {
    return [];
  }
  return text
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);
};

const normalizeSentence = (sentence) => sentence.replace(/\s+/g, ' ').trim().toLowerCase();

const buildFrequencyMap = (words) => {
  const frequency = new Map();
  words.forEach((word) => {
    frequency.set(word, (frequency.get(word) || 0) + 1);
  });
  return frequency;
};

const formatDisplayName = (result) => {
  if (!result) return '';
  const name = result.label || result.model || 'Model';
  return `${name}${result.provider ? ` · ${result.provider}` : ''}`;
};

const computeReadingTime = (wordCount) => {
  if (wordCount === 0) {
    return '0 sec';
  }
  const minutes = wordCount / WORDS_PER_MINUTE;
  if (minutes < 1) {
    return (Math.round(minutes * 60) || 1).toString() + ' sec';
  }
  return minutes.toFixed(1) + ' min';
};

const buildComparison = (first, second) => {
  const wordsA = extractWords(first.response);
  const wordsB = extractWords(second.response);
  const wordSetA = new Set(wordsA);
  const wordSetB = new Set(wordsB);
  const freqA = buildFrequencyMap(wordsA);
  const freqB = buildFrequencyMap(wordsB);

  const intersection = new Set(
    [...wordSetA].filter((word) => wordSetB.has(word)),
  );
  const union = new Set([...wordSetA, ...wordSetB]);
  const similarity = union.size === 0 ? 0 : (intersection.size / union.size) * 100;

  const sentencesA = extractSentences(first.response);
  const sentencesB = extractSentences(second.response);
  const normalizedSentencesB = new Set(sentencesB.map(normalizeSentence));
  const normalizedSentencesA = new Set(sentencesA.map(normalizeSentence));

  const sharedSentences = sentencesA
    .filter((sentence) => normalizedSentencesB.has(normalizeSentence(sentence)))
    .slice(0, 5);

  const uniqueSentencesA = sentencesA
    .filter((sentence) => !normalizedSentencesB.has(normalizeSentence(sentence)))
    .slice(0, 6);

  const uniqueSentencesB = sentencesB
    .filter((sentence) => !normalizedSentencesA.has(normalizeSentence(sentence)))
    .slice(0, 6);

  const filterKeywords = (word) => word.length >= MIN_KEYWORD_LENGTH;

  const commonKeywords = [...intersection]
    .filter(filterKeywords)
    .map((word) => ({
      word,
      total: (freqA.get(word) || 0) + (freqB.get(word) || 0),
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 10);

  const uniqueKeywordsA = [...wordSetA]
    .filter((word) => !wordSetB.has(word) && filterKeywords(word))
    .map((word) => ({
      word,
      count: freqA.get(word) || 0,
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  const uniqueKeywordsB = [...wordSetB]
    .filter((word) => !wordSetA.has(word) && filterKeywords(word))
    .map((word) => ({
      word,
      count: freqB.get(word) || 0,
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  return {
    similarity: Math.round(similarity),
    sharedSentences,
    uniqueSentencesA,
    uniqueSentencesB,
    commonKeywords,
    uniqueKeywordsA,
    uniqueKeywordsB,
    first: {
      displayName: formatDisplayName(first),
      wordCount: wordsA.length,
      charCount: first.response.length,
      tokens: first.tokens,
      readingTime: computeReadingTime(wordsA.length),
      color: first.color,
      raw: first.response,
    },
    second: {
      displayName: formatDisplayName(second),
      wordCount: wordsB.length,
      charCount: second.response.length,
      tokens: second.tokens,
      readingTime: computeReadingTime(wordsB.length),
      color: second.color,
      raw: second.response,
    },
  };
};

const OutputComparisonModal = ({ results, onClose, prompt }) => {
  const comparableResults = useMemo(
    () =>
      results.filter(
        (result) => !result.error && result.response && result.response.trim().length > 0,
      ),
    [results],
  );

  const [primaryIndex, setPrimaryIndex] = useState(0);
  const [secondaryIndex, setSecondaryIndex] = useState(1);
  const [activeTab, setActiveTab] = useState('technical'); // 'technical' or 'ai'
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  useEffect(() => {
    if (comparableResults.length < 2) {
      setPrimaryIndex(0);
      setSecondaryIndex(1);
      return;
    }

    setPrimaryIndex((prev) => (prev < comparableResults.length ? prev : 0));
    setSecondaryIndex((prev) => {
      if (prev < comparableResults.length && prev !== primaryIndex) {
        return prev;
      }
      const fallback = comparableResults.findIndex((_, idx) => idx !== primaryIndex);
      return fallback === -1 ? 0 : fallback;
    });
  }, [comparableResults, primaryIndex]);

  const options = useMemo(
    () =>
      comparableResults.map((result, idx) => ({
        value: idx,
        label: formatDisplayName(result),
      })),
    [comparableResults],
  );

  const comparison = useMemo(() => {
    if (
      comparableResults.length < 2 ||
      primaryIndex === secondaryIndex ||
      !comparableResults[primaryIndex] ||
      !comparableResults[secondaryIndex]
    ) {
      return null;
    }
    return buildComparison(comparableResults[primaryIndex], comparableResults[secondaryIndex]);
  }, [comparableResults, primaryIndex, secondaryIndex]);

  const handlePrimaryChange = (event) => {
    const value = Number(event.target.value);
    setPrimaryIndex(value);
    if (value === secondaryIndex) {
      const fallback = options.find((option) => option.value !== value);
      if (fallback) {
        setSecondaryIndex(fallback.value);
      }
    }
  };

  const handleSecondaryChange = (event) => {
    const value = Number(event.target.value);
    setSecondaryIndex(value);
    if (value === primaryIndex) {
      const fallback = options.find((option) => option.value !== value);
      if (fallback) {
        setPrimaryIndex(fallback.value);
      }
    }
  };

  const loadAiAnalysis = async () => {
    if (comparableResults.length < 2) return;
    
    setIsLoadingAnalysis(true);
    setAnalysisError(null);
    
    try {
      const response = await chatApi.analyzeComparison({
        prompt: prompt || '',
        outputs: comparableResults.map(result => ({
          provider: result.provider,
          model: result.model,
          label: formatDisplayName(result),
          response: result.response,
        })),
      });
      
      setAiAnalysis(response.data.analysis);
    } catch (error) {
      console.error('Failed to load AI analysis:', error);
      setAnalysisError(error.response?.data?.error || 'Failed to generate AI analysis');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  // Load AI analysis when switching to AI tab
  useEffect(() => {
    if (activeTab === 'ai' && !aiAnalysis && !isLoadingAnalysis && !analysisError) {
      loadAiAnalysis();
    }
  }, [activeTab]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal comparison-modal" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <h2>Compare Outputs</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>
        
        {/* Tab Navigation */}
        <div className="comparison-tabs">
          <button
            className={`tab-button ${activeTab === 'technical' ? 'active' : ''}`}
            onClick={() => setActiveTab('technical')}
          >
            Technical Comparison
          </button>
          <button
            className={`tab-button ${activeTab === 'ai' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai')}
            disabled={comparableResults.length < 2}
          >
            AI Analysis ({comparableResults.length} outputs)
          </button>
        </div>

        <div className="modal-content comparison-analysis">
          {prompt && (
            <div className="prompt-summary">
              <strong>Prompt:</strong> <span>{prompt}</span>
            </div>
          )}

          {results.length > comparableResults.length && (
            <div className="comparison-alert">
              One or more responses were unavailable or returned errors and were excluded from the
              analysis.
            </div>
          )}

          {/* Technical Comparison Tab */}
          {activeTab === 'technical' && (
            <>
              {comparableResults.length < 2 ? (
                <div className="comparison-empty">
                  <p>At least two completed responses are required to generate a comparison.</p>
                </div>
              ) : (
                <>
                  <div className="comparison-selectors">
                <div className="selector-group">
                  <label>Primary response</label>
                  <select
                    className="select-input"
                    value={primaryIndex}
                    onChange={handlePrimaryChange}
                  >
                    {options.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="selector-group">
                  <label>Compare against</label>
                  <select
                    className="select-input"
                    value={secondaryIndex}
                    onChange={handleSecondaryChange}
                  >
                    {options.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {comparison ? (
                <>
                  <div className="comparison-metrics">
                    <div className="metric-card">
                      <h4>{comparison.first.displayName}</h4>
                      <div className="metric-value">{comparison.first.wordCount} words</div>
                      <div className="metric-subtext">
                        {comparison.first.charCount} characters · approx {comparison.first.readingTime}
                        {comparison.first.tokens > 0 && ` · ${comparison.first.tokens} tokens`}
                      </div>
                    </div>
                    <div className="metric-card">
                      <h4>{comparison.second.displayName}</h4>
                      <div className="metric-value">{comparison.second.wordCount} words</div>
                      <div className="metric-subtext">
                        {comparison.second.charCount} characters · approx {comparison.second.readingTime}
                        {comparison.second.tokens > 0 && ` · ${comparison.second.tokens} tokens`}
                      </div>
                    </div>
                    <div className="metric-card highlight">
                      <h4>Similarity</h4>
                      <div className="metric-value">{comparison.similarity}% overlap</div>
                      <div className="metric-subtext">
                        {comparison.commonKeywords.length > 0
                          ? 'Top shared keywords highlighted below.'
                          : 'No significant keyword overlap detected.'}
                      </div>
                    </div>
                  </div>

                  {comparison.commonKeywords.length > 0 && (
                    <div className="comparison-section">
                      <h3>Shared keywords</h3>
                      <div className="keyword-chips">
                        {comparison.commonKeywords.map((keyword) => (
                          <span key={`common-${keyword.word}`} className="keyword-chip">
                            <strong>{keyword.word}</strong>
                            <span>{keyword.total}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="comparison-section">
                    <h3>Shared highlights</h3>
                    {comparison.sharedSentences.length === 0 ? (
                      <p>No overlapping sentences detected.</p>
                    ) : (
                      <ul>
                        {comparison.sharedSentences.map((sentence, index) => (
                          <li key={`shared-${index}`}>{sentence}</li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <div className="comparison-section comparison-unique-grid">
                    <div>
                      <h3>Unique to {comparison.first.displayName}</h3>
                      {comparison.uniqueKeywordsA.length > 0 && (
                        <div className="keyword-chips">
                          {comparison.uniqueKeywordsA.map((keyword) => (
                            <span key={`unique-a-${keyword.word}`} className="keyword-chip">
                              <strong>{keyword.word}</strong>
                              <span>{keyword.count}</span>
                            </span>
                          ))}
                        </div>
                      )}
                      {comparison.uniqueSentencesA.length === 0 ? (
                        <p>Mostly overlaps with the comparison response.</p>
                      ) : (
                        <ul>
                          {comparison.uniqueSentencesA.map((sentence, index) => (
                            <li key={`unique-a-${index}`}>{sentence}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <div>
                      <h3>Unique to {comparison.second.displayName}</h3>
                      {comparison.uniqueKeywordsB.length > 0 && (
                        <div className="keyword-chips">
                          {comparison.uniqueKeywordsB.map((keyword) => (
                            <span key={`unique-b-${keyword.word}`} className="keyword-chip">
                              <strong>{keyword.word}</strong>
                              <span>{keyword.count}</span>
                            </span>
                          ))}
                        </div>
                      )}
                      {comparison.uniqueSentencesB.length === 0 ? (
                        <p>Mostly overlaps with the comparison response.</p>
                      ) : (
                        <ul>
                          {comparison.uniqueSentencesB.map((sentence, index) => (
                            <li key={`unique-b-${index}`}>{sentence}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>

                  <div className="comparison-section">
                    <h3>Full responses</h3>
                    <div className="comparison-output-grid">
                      <div className="comparison-output-panel">
                        <h4>{comparison.first.displayName}</h4>
                        <div className="comparison-output-content">
                          <MarkdownMessage content={comparison.first.raw} />
                        </div>
                      </div>
                      <div className="comparison-output-panel">
                        <h4>{comparison.second.displayName}</h4>
                        <div className="comparison-output-content">
                          <MarkdownMessage content={comparison.second.raw} />
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="comparison-empty">
                  <p>Select two different responses to generate a comparison.</p>
                </div>
              )}
            </>
              )}
            </>
          )}

          {/* AI Analysis Tab */}
          {activeTab === 'ai' && (
            <div className="ai-analysis-container">
              {isLoadingAnalysis && (
                <div className="analysis-loading">
                  <div className="spinner"></div>
                  <p>Generating AI analysis of {comparableResults.length} outputs...</p>
                  <p className="analysis-subtext">This may take 10-30 seconds depending on response length.</p>
                </div>
              )}

              {analysisError && (
                <div className="error-banner">
                  <p>⚠️ {analysisError}</p>
                  <button className="btn btn-secondary" onClick={loadAiAnalysis}>
                    Retry Analysis
                  </button>
                </div>
              )}

              {aiAnalysis && !isLoadingAnalysis && (
                <div className="ai-analysis-content">
                  <div className="analysis-header">
                    <h3>AI-Powered Comparison Analysis</h3>
                    <p className="analysis-note">
                      Analyzing {comparableResults.length} model outputs using GPT-4o
                    </p>
                    <button 
                      className="btn btn-secondary btn-sm" 
                      onClick={loadAiAnalysis}
                      disabled={isLoadingAnalysis}
                    >
                      🔄 Regenerate Analysis
                    </button>
                  </div>
                  <div className="analysis-markdown">
                    <MarkdownMessage content={aiAnalysis} />
                  </div>
                </div>
              )}

              {!isLoadingAnalysis && !aiAnalysis && !analysisError && (
                <div className="comparison-empty">
                  <p>Click "AI Analysis" tab to generate a comprehensive comparison.</p>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default OutputComparisonModal;

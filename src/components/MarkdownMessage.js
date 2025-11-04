import React, { useState, useMemo, memo, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MarkdownMessage = memo(({ content }) => {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = useCallback((text, index) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    }).catch((err) => {
      console.error('Failed to copy:', err);
    });
  }, []);

  // Memoize markdown components to avoid re-creating them on every render
  const markdownComponents = useMemo(() => ({
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const codeString = String(children).replace(/\n$/, '');
      const language = match ? match[1] : '';
      const index = `${language}-${codeString.slice(0, 20)}`;

      return !inline && match ? (
        <div className="code-block-wrapper" style={{ position: 'relative', marginBottom: '1rem' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#1e1e1e',
            padding: '0.5rem 1rem',
            borderTopLeftRadius: '0.5rem',
            borderTopRightRadius: '0.5rem',
            fontSize: '0.875rem',
            color: '#d4d4d4',
          }}>
            <span>{language}</span>
            <button
              onClick={() => copyToClipboard(codeString, index)}
              style={{
                backgroundColor: 'transparent',
                border: '1px solid #444',
                borderRadius: '0.25rem',
                padding: '0.25rem 0.75rem',
                color: '#d4d4d4',
                cursor: 'pointer',
                fontSize: '0.875rem',
              }}
            >
              {copiedIndex === index ? '✓ Copied!' : 'Copy'}
            </button>
          </div>
          <SyntaxHighlighter
            style={vscDarkPlus}
            language={language}
            PreTag="div"
            customStyle={{
              margin: 0,
              borderTopLeftRadius: 0,
              borderTopRightRadius: 0,
            }}
            {...props}
          >
            {codeString}
          </SyntaxHighlighter>
        </div>
      ) : (
        <code className={className} style={{
          backgroundColor: '#2d2d2d',
          padding: '0.2rem 0.4rem',
          borderRadius: '0.25rem',
          fontSize: '0.9em',
        }} {...props}>
          {children}
        </code>
      );
    },
    // Style tables
    table({ children }) {
      return (
        <div style={{ overflowX: 'auto', marginBottom: '1rem' }}>
          <table style={{
            borderCollapse: 'collapse',
            width: '100%',
            border: '1px solid #444',
          }}>
            {children}
          </table>
        </div>
      );
    },
    th({ children }) {
      return (
        <th style={{
          backgroundColor: '#2d2d2d',
          padding: '0.75rem',
          textAlign: 'left',
          borderBottom: '2px solid #444',
        }}>
          {children}
        </th>
      );
    },
    td({ children }) {
      return (
        <td style={{
          padding: '0.75rem',
          borderBottom: '1px solid #333',
        }}>
          {children}
        </td>
      );
    },
    // Style lists
    ul({ children }) {
      return (
        <ul style={{
          marginLeft: '1.5rem',
          marginBottom: '1rem',
        }}>
          {children}
        </ul>
      );
    },
    ol({ children }) {
      return (
        <ol style={{
          marginLeft: '1.5rem',
          marginBottom: '1rem',
        }}>
          {children}
        </ol>
      );
    },
    // Style blockquotes
    blockquote({ children }) {
      return (
        <blockquote style={{
          borderLeft: '4px solid #444',
          paddingLeft: '1rem',
          marginLeft: 0,
          marginBottom: '1rem',
          color: '#aaa',
        }}>
          {children}
        </blockquote>
      );
    },
    // Style paragraphs
    p({ children }) {
      return (
        <p style={{
          marginBottom: '1rem',
        }}>
          {children}
        </p>
      );
    },
    // Style headings
    h1({ children }) {
      return (
        <h1 style={{
          fontSize: '1.75rem',
          fontWeight: 'bold',
          marginBottom: '1rem',
          marginTop: '1.5rem',
        }}>
          {children}
        </h1>
      );
    },
    h2({ children }) {
      return (
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: 'bold',
          marginBottom: '0.75rem',
          marginTop: '1.25rem',
        }}>
          {children}
        </h2>
      );
    },
    h3({ children }) {
      return (
        <h3 style={{
          fontSize: '1.25rem',
          fontWeight: 'bold',
          marginBottom: '0.5rem',
          marginTop: '1rem',
        }}>
          {children}
        </h3>
      );
    },
  }), [copiedIndex, copyToClipboard]);

  return (
    <div className="markdown-message">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
});

MarkdownMessage.displayName = 'MarkdownMessage';

export default MarkdownMessage;

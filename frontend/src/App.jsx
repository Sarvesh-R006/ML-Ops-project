import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, XCircle, Search, Cpu } from 'lucide-react';
import './index.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [skills, setSkills] = useState([]);
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [files, setFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState([]);
  const fileInputRef = useRef(null);

  // Fetch available skills on load
  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const res = await axios.get(`${API_BASE}/skills`);
        if (res.data["Programming Languages"]) {
          setSkills(res.data["Programming Languages"]);
        }
      } catch (error) {
        console.error("Failed to fetch skills", error);
      }
    };
    fetchSkills();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
    }
  };

  const toggleSkill = (skill) => {
    setSelectedSkills(prev => 
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    );
  };

  const analyzeResumes = async () => {
    if (files.length === 0) return;
    
    setIsAnalyzing(true);
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    if (selectedSkills.length > 0) {
      formData.append('selected_skills', selectedSkills.join(','));
    }

    try {
      const res = await axios.post(`${API_BASE}/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      // Sort by match score descending
      const sortedResults = res.data.results.sort((a, b) => b.match_score - a.match_score);
      setResults(sortedResults);
    } catch (error) {
      console.error("Error analyzing resumes", error);
      alert("Failed to analyze resumes. Ensure backend is running.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Metrics calculations
  const totalAnalyzed = results.length;
  const eligibleCount = results.filter(r => r.is_eligible).length;
  const avgMatch = totalAnalyzed > 0 
    ? Math.round(results.reduce((acc, curr) => acc + curr.match_score, 0) / totalAnalyzed) 
    : 0;

  return (
    <div className="app-container">
      <header>
        <h1 className="title">ResumeAnalyzer.ai</h1>
        <p className="subtitle">Instant, intelligent parsing & scoring for engineering talent.</p>
      </header>

      {/* Sidebar Controls */}
      <aside className="sidebar">
        <div className="panel">
          <h2><Upload size={20} /> 1. Upload Resumes</h2>
          <div 
            className="upload-area"
            onClick={() => fileInputRef.current.click()}
          >
            <input 
              type="file" 
              multiple 
              accept=".pdf,.docx,.txt"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <FileText size={32} className="upload-icon" />
            <div className="upload-text">
              {files.length > 0 
                ? `${files.length} file(s) selected` 
                : 'Click to upload PDF, DOCX, or TXT'}
            </div>
          </div>
        </div>

        <div className="panel">
          <h2><Cpu size={20} /> 2. Required Languages</h2>
          <div className="skills-container">
            {skills.map(skill => (
              <div 
                key={skill}
                className={`skill-tag ${selectedSkills.includes(skill) ? 'selected' : ''}`}
                onClick={() => toggleSkill(skill)}
              >
                {skill}
              </div>
            ))}
          </div>
        </div>

        <button 
          className="btn-primary"
          onClick={analyzeResumes}
          disabled={isAnalyzing || files.length === 0}
        >
          {isAnalyzing ? <div className="loader"></div> : <><Search size={20} /> Analyze Candidates</>}
        </button>
      </aside>

      {/* Main Results Area */}
      <main className="results-area">
        {results.length === 0 ? (
          <div className="panel empty-state">
            <Search size={64} className="empty-icon" />
            <h2>No Data Yet</h2>
            <p>Upload resumes and click "Analyze Candidates" to view rankings and metrics here.</p>
          </div>
        ) : (
          <>
            <div className="metrics-grid">
              <div className="metric-card">
                <span className="metric-label">Total Resumes</span>
                <span className="metric-value">{totalAnalyzed}</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Eligible</span>
                <span className="metric-value highlight">{eligibleCount}</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Avg Match Score</span>
                <span className="metric-value">{avgMatch}%</span>
              </div>
            </div>

            <div className="panel">
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Candidate</th>
                      <th>Contact</th>
                      <th>Education</th>
                      <th>Match %</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r, i) => (
                      <tr key={i}>
                        <td>
                          <div style={{ fontWeight: 600 }}>{r.Name}</div>
                          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{r.Filename}</div>
                        </td>
                        <td>
                          <div style={{ fontSize: '0.9rem' }}>{r.Email}</div>
                          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{r.Phone}</div>
                        </td>
                        <td>
                          <div style={{ fontSize: '0.9rem' }}>{r.Degree} in {r.Branch}</div>
                          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{r.College} • {r.Year}</div>
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: r.match_score >= 50 ? 'var(--success)' : 'inherit' }}>
                            {r.match_score}%
                          </div>
                        </td>
                        <td>
                          {r.is_eligible ? (
                            <span className="status-badge eligible"><CheckCircle size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }}/> Eligible</span>
                          ) : (
                            <span className="status-badge ineligible"><XCircle size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }}/> Not Eligible</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;

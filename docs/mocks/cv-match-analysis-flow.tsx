import React, { useState } from "react";
import {
  Upload,
  FileText,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Brain,
  CheckCircle2,
  AlertCircle,
  Download,
  Copy,
  ChevronRight,
  Target,
  Zap,
  TrendingUp,
  X,
} from "lucide-react";

const CVMatchAnalysisFlow = () => {
  const [step, setStep] = useState(1); // 1: upload, 2: job desc, 3: processing, 4: results
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [dragActive, setDragActive] = useState(false);

  // Mock results data
  const mockResults = {
    score: 92,
    improvements: [
      {
        category: "Experiência Profissional",
        priority: "high",
        items: [
          'Adicione métricas quantificáveis nas suas conquistas (ex: "Aumentei as vendas em 30%")',
          "Inclua verbos de ação no início de cada bullet point",
          "Destaque projetos relevantes para a vaga",
        ],
      },
      {
        category: "Habilidades Técnicas",
        priority: "medium",
        items: [
          "Adicione: React, TypeScript, Node.js (mencionados na descrição da vaga)",
          "Especifique nível de proficiência em cada tecnologia",
          "Remova habilidades desatualizadas ou irrelevantes",
        ],
      },
      {
        category: "Formatação ATS",
        priority: "low",
        items: [
          "Use fonte padrão (Arial, Calibri ou Times New Roman)",
          "Evite tabelas e colunas múltiplas",
          "Mantenha estrutura de cabeçalhos clara",
        ],
      },
    ],
    keywords: {
      present: ["JavaScript", "Git", "Agile", "SQL", "REST API"],
      missing: [
        "React",
        "TypeScript",
        "Node.js",
        "Docker",
        "CI/CD",
        "AWS",
        "Microservices",
        "GraphQL",
      ],
    },
    atsCompatibility: {
      formatting: 100,
      keywords: 75,
      structure: 90,
    },
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResumeFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  const simulateProcessing = () => {
    setStep(3);
    setTimeout(() => {
      setStep(4);
    }, 3000);
  };

  const getScoreColor = (score) => {
    if (score >= 90) return "var(--primary)";
    if (score >= 80) return "var(--secondary)";
    return "var(--accent)";
  };

  const getPriorityColor = (priority) => {
    if (priority === "high") return "var(--destructive)";
    if (priority === "medium") return "var(--secondary)";
    return "var(--accent)";
  };

  return (
    <>
      <style>{`
        :root {
          --background: oklch(0.9824 0.0013 286.3757);
          --foreground: oklch(0.3211 0 0);
          --card: oklch(1 0 0);
          --primary: oklch(0.6487 0.1538 150.3071);
          --primary-foreground: oklch(1 0 0);
          --secondary: oklch(0.6746 0.1414 261.338);
          --secondary-foreground: oklch(1 0 0);
          --muted: oklch(0.8828 0.0285 98.1033);
          --muted-foreground: oklch(0.5382 0 0);
          --accent: oklch(0.8269 0.108 211.9627);
          --accent-foreground: oklch(0.3211 0 0);
          --destructive: oklch(0.6368 0.2078 25.3313);
          --border: oklch(0.8699 0 0);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .spin { animation: spin 2s linear infinite; }
        .pulse { animation: pulse 2s ease-in-out infinite; }
      `}</style>

      <div
        style={{
          minHeight: "100vh",
          backgroundColor: "var(--background)",
          padding: "2rem 1rem",
        }}
      >
        <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
          {/* Header with Back Button */}
          {step !== 4 && (
            <div style={{ marginBottom: "2rem" }}>
              <button
                onClick={() => step > 1 && setStep(step - 1)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  backgroundColor: "transparent",
                  border: "none",
                  color: "var(--muted-foreground)",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                  fontWeight: "500",
                }}
              >
                <ArrowLeft style={{ width: "16px", height: "16px" }} />
                Voltar
              </button>
            </div>
          )}

          {/* Progress Steps */}
          {step !== 4 && (
            <div style={{ marginBottom: "3rem" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem",
                  marginBottom: "1rem",
                }}
              >
                {[1, 2, 3].map((num) => (
                  <React.Fragment key={num}>
                    <div
                      style={{
                        width: step >= num ? "40px" : "32px",
                        height: step >= num ? "40px" : "32px",
                        borderRadius: "50%",
                        backgroundColor:
                          step >= num ? "var(--primary)" : "var(--muted)",
                        color:
                          step >= num
                            ? "var(--primary-foreground)"
                            : "var(--muted-foreground)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontWeight: "bold",
                        fontSize: step >= num ? "1rem" : "0.875rem",
                        transition: "all 0.3s",
                      }}
                    >
                      {num}
                    </div>
                    {num < 3 && (
                      <div
                        style={{
                          width: "60px",
                          height: "2px",
                          backgroundColor:
                            step > num ? "var(--primary)" : "var(--muted)",
                          transition: "all 0.3s",
                        }}
                      />
                    )}
                  </React.Fragment>
                ))}
              </div>
              <div
                style={{
                  textAlign: "center",
                  fontSize: "0.875rem",
                  color: "var(--muted-foreground)",
                }}
              >
                {step === 1 && "Upload do Currículo"}
                {step === 2 && "Descrição da Vaga"}
                {step === 3 && "Processando com IA"}
              </div>
            </div>
          )}

          {/* Step 1: Resume Upload */}
          {step === 1 && (
            <div style={{ maxWidth: "600px", margin: "0 auto" }}>
              <div style={{ textAlign: "center", marginBottom: "2rem" }}>
                <h1
                  style={{
                    fontSize: "clamp(1.5rem, 4vw, 2rem)",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                    marginBottom: "0.5rem",
                  }}
                >
                  Envie seu currículo
                </h1>
                <p
                  style={{ fontSize: "1rem", color: "var(--muted-foreground)" }}
                >
                  Formatos aceitos: PDF ou DOCX (máx. 5MB)
                </p>
              </div>

              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                style={{
                  padding: "3rem 2rem",
                  border: `2px dashed ${dragActive ? "var(--primary)" : "var(--border)"}`,
                  borderRadius: "16px",
                  backgroundColor: dragActive
                    ? "color-mix(in oklch, var(--primary) 5%, transparent)"
                    : "var(--card)",
                  textAlign: "center",
                  cursor: "pointer",
                  transition: "all 0.3s",
                }}
              >
                {!resumeFile ? (
                  <>
                    <Upload
                      style={{
                        width: "64px",
                        height: "64px",
                        color: dragActive
                          ? "var(--primary)"
                          : "var(--muted-foreground)",
                        margin: "0 auto 1.5rem",
                        transition: "all 0.3s",
                      }}
                    />
                    <h3
                      style={{
                        fontSize: "1.125rem",
                        fontWeight: "600",
                        color: "var(--foreground)",
                        marginBottom: "0.5rem",
                      }}
                    >
                      {dragActive
                        ? "Solte o arquivo aqui"
                        : "Arraste seu currículo aqui"}
                    </h3>
                    <p
                      style={{
                        fontSize: "0.875rem",
                        color: "var(--muted-foreground)",
                        marginBottom: "1.5rem",
                      }}
                    >
                      ou clique para selecionar
                    </p>
                    <input
                      type="file"
                      accept=".pdf,.docx"
                      onChange={handleFileChange}
                      style={{ display: "none" }}
                      id="resume-upload"
                    />
                    <label htmlFor="resume-upload">
                      <button
                        onClick={() =>
                          document.getElementById("resume-upload").click()
                        }
                        style={{
                          height: "44px",
                          padding: "0 2rem",
                          backgroundColor: "var(--primary)",
                          color: "var(--primary-foreground)",
                          border: "none",
                          borderRadius: "8px",
                          fontWeight: "600",
                          cursor: "pointer",
                          fontSize: "0.875rem",
                        }}
                      >
                        Selecionar Arquivo
                      </button>
                    </label>
                  </>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "1.5rem",
                      backgroundColor:
                        "color-mix(in oklch, var(--primary) 5%, transparent)",
                      borderRadius: "12px",
                      border: "1px solid var(--primary)",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "1rem",
                      }}
                    >
                      <div
                        style={{
                          width: "48px",
                          height: "48px",
                          backgroundColor: "var(--primary)",
                          borderRadius: "8px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <FileText
                          style={{
                            width: "24px",
                            height: "24px",
                            color: "var(--primary-foreground)",
                          }}
                        />
                      </div>
                      <div style={{ textAlign: "left" }}>
                        <div
                          style={{
                            fontSize: "0.875rem",
                            fontWeight: "600",
                            color: "var(--foreground)",
                          }}
                        >
                          {resumeFile.name}
                        </div>
                        <div
                          style={{
                            fontSize: "0.75rem",
                            color: "var(--muted-foreground)",
                          }}
                        >
                          {(resumeFile.size / 1024).toFixed(0)} KB
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setResumeFile(null)}
                      style={{
                        width: "32px",
                        height: "32px",
                        backgroundColor: "transparent",
                        border: "none",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <X
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "var(--muted-foreground)",
                        }}
                      />
                    </button>
                  </div>
                )}
              </div>

              {resumeFile && (
                <button
                  onClick={() => setStep(2)}
                  style={{
                    width: "100%",
                    height: "48px",
                    marginTop: "1.5rem",
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: "600",
                    cursor: "pointer",
                    fontSize: "1rem",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "0.5rem",
                    boxShadow:
                      "0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)",
                  }}
                >
                  Continuar
                  <ArrowRight style={{ width: "20px", height: "20px" }} />
                </button>
              )}
            </div>
          )}

          {/* Step 2: Job Description */}
          {step === 2 && (
            <div style={{ maxWidth: "800px", margin: "0 auto" }}>
              <div style={{ textAlign: "center", marginBottom: "2rem" }}>
                <h1
                  style={{
                    fontSize: "clamp(1.5rem, 4vw, 2rem)",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                    marginBottom: "0.5rem",
                  }}
                >
                  Cole a descrição da vaga
                </h1>
                <p
                  style={{ fontSize: "1rem", color: "var(--muted-foreground)" }}
                >
                  Quanto mais detalhes, melhor será a otimização
                </p>
              </div>

              <div
                style={{
                  padding: "1.5rem",
                  backgroundColor: "var(--card)",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                }}
              >
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Cole aqui a descrição completa da vaga, incluindo requisitos, responsabilidades e qualificações desejadas..."
                  style={{
                    width: "100%",
                    minHeight: "300px",
                    padding: "1rem",
                    fontSize: "0.875rem",
                    lineHeight: "1.6",
                    color: "var(--foreground)",
                    backgroundColor: "var(--background)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    resize: "vertical",
                    fontFamily: "inherit",
                  }}
                />
                <div
                  style={{
                    marginTop: "1rem",
                    padding: "1rem",
                    backgroundColor:
                      "color-mix(in oklch, var(--accent) 5%, transparent)",
                    borderRadius: "8px",
                    border:
                      "1px solid color-mix(in oklch, var(--accent) 20%, transparent)",
                    display: "flex",
                    gap: "0.75rem",
                  }}
                >
                  <AlertCircle
                    style={{
                      width: "20px",
                      height: "20px",
                      color: "var(--accent-foreground)",
                      flexShrink: 0,
                    }}
                  />
                  <div
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--muted-foreground)",
                      lineHeight: "1.5",
                    }}
                  >
                    <strong style={{ color: "var(--foreground)" }}>
                      Dica:
                    </strong>{" "}
                    Inclua toda a descrição da vaga para resultados mais
                    precisos. Nossa IA identificará as palavras-chave mais
                    importantes automaticamente.
                  </div>
                </div>
              </div>

              <button
                onClick={simulateProcessing}
                disabled={!jobDescription || jobDescription.length < 50}
                style={{
                  width: "100%",
                  height: "48px",
                  marginTop: "1.5rem",
                  backgroundColor:
                    !jobDescription || jobDescription.length < 50
                      ? "var(--muted)"
                      : "var(--primary)",
                  color: "var(--primary-foreground)",
                  border: "none",
                  borderRadius: "8px",
                  fontWeight: "600",
                  cursor:
                    !jobDescription || jobDescription.length < 50
                      ? "not-allowed"
                      : "pointer",
                  fontSize: "1rem",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem",
                  opacity:
                    !jobDescription || jobDescription.length < 50 ? 0.5 : 1,
                }}
              >
                <Sparkles style={{ width: "20px", height: "20px" }} />
                Analisar com IA
              </button>
            </div>
          )}

          {/* Step 3: Processing */}
          {step === 3 && (
            <div
              style={{
                maxWidth: "600px",
                margin: "0 auto",
                textAlign: "center",
                padding: "4rem 0",
              }}
            >
              <div
                className="spin"
                style={{
                  width: "80px",
                  height: "80px",
                  margin: "0 auto 2rem",
                  borderRadius: "50%",
                  border: "4px solid var(--muted)",
                  borderTopColor: "var(--primary)",
                }}
              />
              <h2
                style={{
                  fontSize: "1.5rem",
                  fontWeight: "bold",
                  color: "var(--foreground)",
                  marginBottom: "1rem",
                }}
              >
                Analisando seu currículo...
              </h2>
              <p
                style={{
                  fontSize: "1rem",
                  color: "var(--muted-foreground)",
                  marginBottom: "2rem",
                }}
              >
                Nossa IA está comparando seu currículo com a descrição da vaga
              </p>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                  textAlign: "left",
                  maxWidth: "400px",
                  margin: "0 auto",
                }}
              >
                {[
                  { text: "Extraindo texto do currículo", done: true },
                  { text: "Identificando palavras-chave", done: true },
                  { text: "Analisando compatibilidade ATS", done: false },
                  { text: "Gerando sugestões personalizadas", done: false },
                ].map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      padding: "0.75rem 1rem",
                      backgroundColor: "var(--card)",
                      borderRadius: "8px",
                      border: "1px solid var(--border)",
                    }}
                  >
                    {item.done ? (
                      <CheckCircle2
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "var(--primary)",
                        }}
                      />
                    ) : (
                      <div
                        className="pulse"
                        style={{
                          width: "20px",
                          height: "20px",
                          borderRadius: "50%",
                          backgroundColor: "var(--primary)",
                        }}
                      />
                    )}
                    <span
                      style={{
                        fontSize: "0.875rem",
                        color: "var(--foreground)",
                      }}
                    >
                      {item.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: Results */}
          {step === 4 && (
            <div>
              {/* Header */}
              <div
                style={{
                  textAlign: "center",
                  marginBottom: "3rem",
                  padding: "2rem",
                  backgroundColor: "var(--card)",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                }}
              >
                <div
                  style={{
                    width: "120px",
                    height: "120px",
                    margin: "0 auto 1.5rem",
                    position: "relative",
                  }}
                >
                  <svg
                    style={{
                      width: "100%",
                      height: "100%",
                      transform: "rotate(-90deg)",
                    }}
                  >
                    <circle
                      cx="50%"
                      cy="50%"
                      r="45%"
                      stroke="var(--muted)"
                      strokeWidth="10"
                      fill="none"
                    />
                    <circle
                      cx="50%"
                      cy="50%"
                      r="45%"
                      stroke={getScoreColor(mockResults.score)}
                      strokeWidth="10"
                      fill="none"
                      strokeDasharray="283"
                      strokeDashoffset={283 - (283 * mockResults.score) / 100}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "2.5rem",
                        fontWeight: "bold",
                        color: "var(--foreground)",
                      }}
                    >
                      {mockResults.score}
                    </span>
                    <span
                      style={{
                        fontSize: "0.875rem",
                        color: "var(--muted-foreground)",
                      }}
                    >
                      de 100
                    </span>
                  </div>
                </div>

                <h1
                  style={{
                    fontSize: "1.75rem",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                    marginBottom: "0.5rem",
                  }}
                >
                  Excelente compatibilidade!
                </h1>
                <p
                  style={{
                    fontSize: "1rem",
                    color: "var(--muted-foreground)",
                    marginBottom: "1.5rem",
                  }}
                >
                  Seu currículo tem alta chance de passar pelo ATS
                </p>

                <div
                  style={{
                    display: "flex",
                    gap: "1rem",
                    justifyContent: "center",
                    flexWrap: "wrap",
                  }}
                >
                  <button
                    style={{
                      height: "44px",
                      padding: "0 1.5rem",
                      backgroundColor: "var(--primary)",
                      color: "var(--primary-foreground)",
                      border: "none",
                      borderRadius: "8px",
                      fontWeight: "600",
                      cursor: "pointer",
                      fontSize: "0.875rem",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <Download style={{ width: "18px", height: "18px" }} />
                    Baixar Otimizado
                  </button>
                  <button
                    style={{
                      height: "44px",
                      padding: "0 1.5rem",
                      backgroundColor: "transparent",
                      color: "var(--primary)",
                      border: "1px solid var(--primary)",
                      borderRadius: "8px",
                      fontWeight: "600",
                      cursor: "pointer",
                      fontSize: "0.875rem",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <Copy style={{ width: "18px", height: "18px" }} />
                    Nova Análise
                  </button>
                </div>
              </div>

              {/* ATS Compatibility Breakdown */}
              <div
                style={{
                  marginBottom: "2rem",
                  padding: "1.5rem",
                  backgroundColor: "var(--card)",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                }}
              >
                <h2
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                    marginBottom: "1.5rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <Target
                    style={{
                      width: "24px",
                      height: "24px",
                      color: "var(--primary)",
                    }}
                  />
                  Compatibilidade ATS
                </h2>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "1rem",
                  }}
                >
                  {Object.entries(mockResults.atsCompatibility).map(
                    ([key, value]) => (
                      <div key={key}>
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            marginBottom: "0.5rem",
                          }}
                        >
                          <span
                            style={{
                              fontSize: "0.875rem",
                              fontWeight: "500",
                              color: "var(--foreground)",
                              textTransform: "capitalize",
                            }}
                          >
                            {key === "formatting"
                              ? "Formatação"
                              : key === "keywords"
                                ? "Palavras-chave"
                                : "Estrutura"}
                          </span>
                          <span
                            style={{
                              fontSize: "0.875rem",
                              fontWeight: "bold",
                              color: getScoreColor(value),
                            }}
                          >
                            {value}%
                          </span>
                        </div>
                        <div
                          style={{
                            width: "100%",
                            height: "8px",
                            backgroundColor: "var(--muted)",
                            borderRadius: "4px",
                            overflow: "hidden",
                          }}
                        >
                          <div
                            style={{
                              width: `${value}%`,
                              height: "100%",
                              backgroundColor: getScoreColor(value),
                              transition: "width 1s ease-in-out",
                            }}
                          />
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>

              {/* Keywords Analysis */}
              <div
                style={{
                  marginBottom: "2rem",
                  padding: "1.5rem",
                  backgroundColor: "var(--card)",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                }}
              >
                <h2
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                    marginBottom: "1.5rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <Zap
                    style={{
                      width: "24px",
                      height: "24px",
                      color: "var(--secondary)",
                    }}
                  />
                  Análise de Palavras-chave
                </h2>

                <div
                  style={{
                    display: "grid",
                    gap: "1.5rem",
                    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: "0.875rem",
                        fontWeight: "600",
                        color: "var(--foreground)",
                        marginBottom: "0.75rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                      }}
                    >
                      <CheckCircle2
                        style={{
                          width: "16px",
                          height: "16px",
                          color: "var(--primary)",
                        }}
                      />
                      Presentes ({mockResults.keywords.present.length})
                    </div>
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "0.5rem",
                      }}
                    >
                      {mockResults.keywords.present.map((keyword, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: "0.375rem 0.75rem",
                            backgroundColor:
                              "color-mix(in oklch, var(--primary) 10%, transparent)",
                            color: "var(--primary)",
                            borderRadius: "6px",
                            fontSize: "0.75rem",
                            fontWeight: "500",
                          }}
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        fontSize: "0.875rem",
                        fontWeight: "600",
                        color: "var(--foreground)",
                        marginBottom: "0.75rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                      }}
                    >
                      <AlertCircle
                        style={{
                          width: "16px",
                          height: "16px",
                          color: "var(--destructive)",
                        }}
                      />
                      Ausentes ({mockResults.keywords.missing.length})
                    </div>
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "0.5rem",
                      }}
                    >
                      {mockResults.keywords.missing.map((keyword, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: "0.375rem 0.75rem",
                            backgroundColor:
                              "color-mix(in oklch, var(--destructive) 10%, transparent)",
                            color: "var(--destructive)",
                            borderRadius: "6px",
                            fontSize: "0.75rem",
                            fontWeight: "500",
                          }}
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Improvements */}
              <div
                style={{
                  padding: "1.5rem",
                  backgroundColor: "var(--card)",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                }}
              >
                <h2
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                    marginBottom: "1.5rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <TrendingUp
                    style={{
                      width: "24px",
                      height: "24px",
                      color: "var(--accent-foreground)",
                    }}
                  />
                  Sugestões de Melhoria
                </h2>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "1.5rem",
                  }}
                >
                  {mockResults.improvements.map((improvement, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "1.5rem",
                        backgroundColor: "var(--background)",
                        borderRadius: "12px",
                        border: `1px solid ${getPriorityColor(improvement.priority)}`,
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.75rem",
                          marginBottom: "1rem",
                        }}
                      >
                        <div
                          style={{
                            padding: "0.25rem 0.75rem",
                            backgroundColor: `color-mix(in oklch, ${getPriorityColor(improvement.priority)} 10%, transparent)`,
                            color: getPriorityColor(improvement.priority),
                            borderRadius: "6px",
                            fontSize: "0.75rem",
                            fontWeight: "600",
                            textTransform: "uppercase",
                          }}
                        >
                          {improvement.priority === "high"
                            ? "Alta"
                            : improvement.priority === "medium"
                              ? "Média"
                              : "Baixa"}{" "}
                          Prioridade
                        </div>
                        <h3
                          style={{
                            fontSize: "1rem",
                            fontWeight: "600",
                            color: "var(--foreground)",
                          }}
                        >
                          {improvement.category}
                        </h3>
                      </div>
                      <ul
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.75rem",
                          paddingLeft: "1.5rem",
                        }}
                      >
                        {improvement.items.map((item, itemIdx) => (
                          <li
                            key={itemIdx}
                            style={{
                              fontSize: "0.875rem",
                              color: "var(--muted-foreground)",
                              lineHeight: "1.6",
                            }}
                          >
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CVMatchAnalysisFlow;

import React, { useState, useEffect } from "react";
import {
  Upload,
  CheckCircle2,
  Zap,
  Shield,
  ArrowRight,
  TrendingUp,
  FileCheck,
  Brain,
  Award,
  ChevronDown,
  Lock,
  Sparkles,
  BarChart3,
  Clock,
  Target,
  Users,
  Star,
} from "lucide-react";

const CVMatchLanding = () => {
  const [openFaq, setOpenFaq] = useState(null);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  return (
    <>
      <style>{`
        :root {
          --background: oklch(0.9824 0.0013 286.3757);
          --foreground: oklch(0.3211 0 0);
          --card: oklch(1 0 0);
          --card-foreground: oklch(0.3211 0 0);
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

        .bg-background { background-color: var(--background); }
        .bg-card { background-color: var(--card); }
        .bg-primary { background-color: var(--primary); }
        .bg-secondary { background-color: var(--secondary); }
        .bg-accent { background-color: var(--accent); }
        .bg-muted { background-color: var(--muted); }
        .bg-destructive { background-color: var(--destructive); }

        .text-foreground { color: var(--foreground); }
        .text-primary { color: var(--primary); }
        .text-primary-foreground { color: var(--primary-foreground); }
        .text-secondary { color: var(--secondary); }
        .text-secondary-foreground { color: var(--secondary-foreground); }
        .text-muted-foreground { color: var(--muted-foreground); }
        .text-accent-foreground { color: var(--accent-foreground); }
        .text-destructive { color: var(--destructive); }

        .border-border { border-color: var(--border); }
        .border-primary { border-color: var(--primary); }

        .hover\\:opacity-90:hover { opacity: 0.9; }
        .hover\\:text-foreground:hover { color: var(--foreground); }
        .hover\\:bg-accent:hover { background-color: var(--accent); }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
      `}</style>

      <div
        className="min-h-screen"
        style={{
          backgroundColor: "var(--background)",
          fontFamily: "system-ui, sans-serif",
        }}
      >
        {/* Navigation */}
        <nav
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            zIndex: 50,
            transition: "all 0.3s",
            backgroundColor: isScrolled
              ? "color-mix(in oklch, var(--background) 95%, transparent)"
              : "transparent",
            backdropFilter: isScrolled ? "blur(12px)" : "none",
            borderBottom: isScrolled ? "1px solid var(--border)" : "none",
            boxShadow: isScrolled ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
          }}
        >
          <div
            style={{
              maxWidth: "1280px",
              margin: "0 auto",
              padding: "0 1.5rem",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                height: "64px",
              }}
            >
              <div
                style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
              >
                <div
                  style={{
                    width: "32px",
                    height: "32px",
                    backgroundColor: "var(--primary)",
                    borderRadius: "8px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <FileCheck
                    style={{
                      width: "20px",
                      height: "20px",
                      color: "var(--primary-foreground)",
                    }}
                  />
                </div>
                <span
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: "bold",
                    color: "var(--foreground)",
                  }}
                >
                  CV-Match
                </span>
              </div>
              <div
                style={{ display: "none", gap: "1.5rem", alignItems: "center" }}
                className="md-flex"
              >
                <a
                  href="#como-funciona"
                  style={{
                    fontSize: "0.875rem",
                    fontWeight: "500",
                    color: "var(--muted-foreground)",
                    textDecoration: "none",
                  }}
                >
                  Como Funciona
                </a>
                <a
                  href="#precos"
                  style={{
                    fontSize: "0.875rem",
                    fontWeight: "500",
                    color: "var(--muted-foreground)",
                    textDecoration: "none",
                  }}
                >
                  Preços
                </a>
                <a
                  href="#faq"
                  style={{
                    fontSize: "0.875rem",
                    fontWeight: "500",
                    color: "var(--muted-foreground)",
                    textDecoration: "none",
                  }}
                >
                  FAQ
                </a>
                <button
                  style={{
                    fontSize: "0.875rem",
                    fontWeight: "500",
                    color: "var(--muted-foreground)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Entrar
                </button>
                <button
                  style={{
                    height: "40px",
                    padding: "0 1.5rem",
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                    borderRadius: "8px",
                    fontSize: "0.875rem",
                    fontWeight: "600",
                    border: "none",
                    cursor: "pointer",
                    boxShadow:
                      "0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)",
                  }}
                >
                  Começar Grátis
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section
          style={{
            position: "relative",
            paddingTop: "8rem",
            paddingBottom: "5rem",
            padding: "8rem 1.5rem 5rem",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(to bottom, color-mix(in oklch, var(--primary) 5%, transparent), var(--background))",
            }}
          />

          <div
            style={{
              position: "relative",
              maxWidth: "1280px",
              margin: "0 auto",
            }}
          >
            <div
              style={{
                maxWidth: "896px",
                margin: "0 auto",
                textAlign: "center",
              }}
            >
              {/* Badge */}
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0.5rem 1rem",
                  borderRadius: "9999px",
                  border: "1px solid var(--border)",
                  backgroundColor:
                    "color-mix(in oklch, var(--card) 50%, transparent)",
                  backdropFilter: "blur(4px)",
                  marginBottom: "2rem",
                }}
              >
                <Sparkles
                  style={{
                    width: "16px",
                    height: "16px",
                    color: "var(--primary)",
                  }}
                />
                <span
                  style={{
                    fontSize: "0.875rem",
                    fontWeight: "500",
                    color: "var(--foreground)",
                  }}
                >
                  Inteligência Artificial para o mercado brasileiro
                </span>
              </div>

              {/* Headline */}
              <h1
                style={{
                  fontSize: "clamp(2rem, 5vw, 4rem)",
                  fontWeight: "bold",
                  color: "var(--foreground)",
                  lineHeight: "1.1",
                  marginBottom: "2rem",
                }}
              >
                IA que transforma{" "}
                <span style={{ color: "var(--primary)" }}>currículos</span> em{" "}
                <span style={{ color: "var(--secondary)" }}>entrevistas</span>
              </h1>

              {/* Subheadline */}
              <p
                style={{
                  fontSize: "1.125rem",
                  color: "var(--muted-foreground)",
                  maxWidth: "672px",
                  margin: "0 auto 2rem",
                  lineHeight: "1.75",
                }}
              >
                Passe pelo ATS das melhores empresas brasileiras com análise
                inteligente de palavras-chave e otimização automática
              </p>

              {/* CTAs */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                  alignItems: "center",
                  marginBottom: "2rem",
                }}
              >
                <button
                  style={{
                    width: "100%",
                    maxWidth: "300px",
                    height: "48px",
                    padding: "0 2rem",
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                    borderRadius: "8px",
                    fontWeight: "600",
                    border: "none",
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "0.5rem",
                    boxShadow:
                      "0 10px 15px -3px color-mix(in oklch, var(--primary) 25%, transparent)",
                  }}
                >
                  Começar Gratuitamente
                  <ArrowRight style={{ width: "20px", height: "20px" }} />
                </button>
                <button
                  style={{
                    width: "100%",
                    maxWidth: "300px",
                    height: "48px",
                    padding: "0 2rem",
                    borderRadius: "8px",
                    fontWeight: "600",
                    border: "1px solid var(--border)",
                    backgroundColor: "transparent",
                    color: "var(--foreground)",
                    cursor: "pointer",
                  }}
                >
                  Ver Como Funciona
                </button>
              </div>

              {/* Trust Indicators */}
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "1.5rem",
                  paddingTop: "2rem",
                  fontSize: "0.875rem",
                  color: "var(--muted-foreground)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <Shield
                    style={{
                      width: "16px",
                      height: "16px",
                      color: "var(--primary)",
                    }}
                  />
                  <span>LGPD Compliant</span>
                </div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <Zap
                    style={{
                      width: "16px",
                      height: "16px",
                      color: "var(--primary)",
                    }}
                  />
                  <span>Resultados em 2 minutos</span>
                </div>
                <div
                  style={{
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
                  <span>3 análises grátis</span>
                </div>
              </div>
            </div>

            {/* Hero Visual */}
            <div style={{ maxWidth: "1120px", margin: "4rem auto 0" }}>
              <div
                style={{
                  position: "relative",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                  backgroundColor: "var(--card)",
                  boxShadow: "0 25px 50px -12px rgba(0,0,0,0.25)",
                  padding: "2rem",
                }}
              >
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                    gap: "2rem",
                  }}
                >
                  {/* Score Display */}
                  <div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        marginBottom: "1.5rem",
                      }}
                    >
                      <span
                        style={{
                          fontSize: "0.875rem",
                          fontWeight: "500",
                          color: "var(--muted-foreground)",
                        }}
                      >
                        Compatibilidade ATS
                      </span>
                      <div
                        style={{
                          padding: "0.25rem 0.75rem",
                          borderRadius: "6px",
                          backgroundColor:
                            "color-mix(in oklch, var(--primary) 10%, transparent)",
                          color: "var(--primary)",
                          fontSize: "0.75rem",
                          fontWeight: "600",
                        }}
                      >
                        Análise Completa
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        padding: "1.5rem 0",
                      }}
                    >
                      <div
                        style={{
                          position: "relative",
                          width: "144px",
                          height: "144px",
                          marginBottom: "1rem",
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
                            stroke="color-mix(in oklch, var(--muted) 20%, transparent)"
                            strokeWidth="8"
                            fill="none"
                          />
                          <circle
                            cx="50%"
                            cy="50%"
                            r="45%"
                            stroke="var(--primary)"
                            strokeWidth="8"
                            fill="none"
                            strokeDasharray="283"
                            strokeDashoffset="28"
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
                              fontSize: "3rem",
                              fontWeight: "bold",
                              color: "var(--foreground)",
                            }}
                          >
                            92
                          </span>
                          <span
                            style={{
                              fontSize: "0.75rem",
                              color: "var(--muted-foreground)",
                            }}
                          >
                            de 100
                          </span>
                        </div>
                      </div>
                      <div style={{ textAlign: "center" }}>
                        <div
                          style={{
                            fontSize: "1rem",
                            fontWeight: "600",
                            color: "var(--foreground)",
                          }}
                        >
                          Excelente Match
                        </div>
                        <div
                          style={{
                            fontSize: "0.875rem",
                            color: "var(--muted-foreground)",
                          }}
                        >
                          Alta chance de aprovação
                        </div>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.5rem",
                      }}
                    >
                      {[
                        {
                          icon: CheckCircle2,
                          label: "Formatação ATS",
                          value: "100%",
                          color: "primary",
                        },
                        {
                          icon: CheckCircle2,
                          label: "Palavras-chave",
                          value: "+18",
                          color: "primary",
                        },
                        {
                          icon: Brain,
                          label: "Melhorias IA",
                          value: "12",
                          color: "secondary",
                        },
                      ].map((item, idx) => {
                        const Icon = item.icon;
                        return (
                          <div
                            key={idx}
                            style={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "space-between",
                              padding: "0.75rem",
                              borderRadius: "8px",
                              backgroundColor: `color-mix(in oklch, var(--${item.color}) 5%, transparent)`,
                              border: `1px solid color-mix(in oklch, var(--${item.color}) 20%, transparent)`,
                            }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.75rem",
                              }}
                            >
                              <Icon
                                style={{
                                  width: "16px",
                                  height: "16px",
                                  color: `var(--${item.color})`,
                                  flexShrink: 0,
                                }}
                              />
                              <span
                                style={{
                                  fontSize: "0.875rem",
                                  fontWeight: "500",
                                  color: "var(--foreground)",
                                }}
                              >
                                {item.label}
                              </span>
                            </div>
                            <span
                              style={{
                                fontSize: "0.75rem",
                                fontWeight: "bold",
                                color: `var(--${item.color})`,
                              }}
                            >
                              {item.value}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Improvements Preview */}
                  <div>
                    <h3
                      style={{
                        fontSize: "0.875rem",
                        fontWeight: "600",
                        color: "var(--foreground)",
                        marginBottom: "1rem",
                      }}
                    >
                      Principais Melhorias
                    </h3>
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.75rem",
                        fontSize: "0.875rem",
                      }}
                    >
                      {[
                        {
                          title: "Experiência Profissional",
                          desc: "Adicionadas métricas quantificáveis em 3 posições",
                        },
                        {
                          title: "Habilidades Técnicas",
                          desc: "Incluídas 8 tecnologias da descrição da vaga",
                        },
                        {
                          title: "Palavras-chave ATS",
                          desc: "Otimizadas 18 palavras para sistemas de rastreamento",
                        },
                      ].map((improvement, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: "1rem",
                            borderRadius: "8px",
                            border: "1px solid var(--border)",
                            backgroundColor:
                              "color-mix(in oklch, var(--background) 50%, transparent)",
                          }}
                        >
                          <div
                            style={{
                              fontWeight: "500",
                              color: "var(--foreground)",
                              marginBottom: "0.25rem",
                            }}
                          >
                            {improvement.title}
                          </div>
                          <div
                            style={{
                              fontSize: "0.75rem",
                              color: "var(--muted-foreground)",
                              lineHeight: "1.5",
                            }}
                          >
                            {improvement.desc}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div
              style={{
                maxWidth: "896px",
                margin: "4rem auto 0",
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "2rem",
              }}
            >
              {[
                { value: "95%", label: "Aprovação ATS" },
                { value: "2min", label: "Análise completa" },
                { value: "3x", label: "Mais entrevistas" },
              ].map((stat, idx) => (
                <div key={idx} style={{ textAlign: "center" }}>
                  <div
                    style={{
                      fontSize: "2.5rem",
                      fontWeight: "bold",
                      marginBottom: "0.5rem",
                      color: "var(--foreground)",
                    }}
                  >
                    {stat.value}
                  </div>
                  <div
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Problem Statement */}
        <section
          style={{
            padding: "5rem 1.5rem",
            backgroundColor:
              "color-mix(in oklch, var(--muted) 30%, transparent)",
          }}
        >
          <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
            <div
              style={{
                maxWidth: "768px",
                margin: "0 auto 4rem",
                textAlign: "center",
              }}
            >
              <h2
                style={{
                  fontSize: "clamp(1.875rem, 4vw, 2.25rem)",
                  fontWeight: "bold",
                  marginBottom: "1rem",
                  color: "var(--foreground)",
                }}
              >
                Por que currículos não geram entrevistas
              </h2>
              <p
                style={{
                  fontSize: "1.125rem",
                  color: "var(--muted-foreground)",
                }}
              >
                Os principais obstáculos que impedem sua aprovação
              </p>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "1.5rem",
              }}
            >
              {[
                {
                  icon: BarChart3,
                  color: "destructive",
                  title: "75% eliminados pelo ATS",
                  desc: "Sistemas automatizados rejeitam currículos antes de um recrutador ver",
                },
                {
                  icon: Clock,
                  color: "accent",
                  title: "20h por semana perdidas",
                  desc: "Profissionais gastam tempo em candidaturas sem resposta",
                },
                {
                  icon: Target,
                  color: "secondary",
                  title: "Palavras-chave ausentes",
                  desc: "Faltam termos estratégicos que sistemas de rastreamento procuram",
                },
              ].map((problem, idx) => {
                const Icon = problem.icon;
                return (
                  <div
                    key={idx}
                    style={{
                      padding: "1.5rem",
                      borderRadius: "16px",
                      border: "1px solid var(--border)",
                      backgroundColor: "var(--card)",
                      transition: "box-shadow 0.3s",
                    }}
                  >
                    <div
                      style={{
                        width: "48px",
                        height: "48px",
                        borderRadius: "12px",
                        backgroundColor: `color-mix(in oklch, var(--${problem.color}) 10%, transparent)`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        marginBottom: "1.5rem",
                      }}
                    >
                      <Icon
                        style={{
                          width: "24px",
                          height: "24px",
                          color: `var(--${problem.color})`,
                        }}
                      />
                    </div>
                    <h3
                      style={{
                        fontSize: "1.125rem",
                        fontWeight: "600",
                        marginBottom: "0.75rem",
                        color: "var(--foreground)",
                      }}
                    >
                      {problem.title}
                    </h3>
                    <p
                      style={{
                        fontSize: "0.875rem",
                        color: "var(--muted-foreground)",
                        lineHeight: "1.5",
                      }}
                    >
                      {problem.desc}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="como-funciona" style={{ padding: "5rem 1.5rem" }}>
          <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
            <div
              style={{
                maxWidth: "768px",
                margin: "0 auto 4rem",
                textAlign: "center",
              }}
            >
              <h2
                style={{
                  fontSize: "clamp(1.875rem, 4vw, 2.25rem)",
                  fontWeight: "bold",
                  marginBottom: "1rem",
                  color: "var(--foreground)",
                }}
              >
                Como funciona
              </h2>
              <p
                style={{
                  fontSize: "1.125rem",
                  color: "var(--muted-foreground)",
                }}
              >
                Três passos simples para otimizar seu currículo
              </p>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "2rem",
                maxWidth: "1120px",
                margin: "0 auto",
              }}
            >
              {[
                {
                  icon: Upload,
                  color: "primary",
                  number: "1",
                  title: "Upload",
                  desc: "Envie seu currículo e cole a descrição da vaga. PDF ou DOCX aceitos.",
                },
                {
                  icon: Brain,
                  color: "secondary",
                  number: "2",
                  title: "Análise IA",
                  desc: "IA identifica gaps, adiciona palavras-chave e otimiza para ATS.",
                },
                {
                  icon: Award,
                  color: "accent",
                  number: "3",
                  title: "Otimizado",
                  desc: "Baixe seu currículo otimizado em PDF ou DOCX editável.",
                },
              ].map((step, idx) => {
                const Icon = step.icon;
                return (
                  <div key={idx} style={{ position: "relative" }}>
                    <div
                      style={{
                        padding: "2rem",
                        borderRadius: "16px",
                        border: "1px solid var(--border)",
                        backgroundColor: "var(--card)",
                      }}
                    >
                      <div
                        style={{
                          width: "56px",
                          height: "56px",
                          borderRadius: "12px",
                          backgroundColor: `var(--${step.color})`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          marginBottom: "1.5rem",
                        }}
                      >
                        <Icon
                          style={{
                            width: "28px",
                            height: "28px",
                            color: `var(--${step.color}-foreground)`,
                          }}
                        />
                      </div>
                      <div
                        style={{
                          position: "absolute",
                          top: "-12px",
                          right: "-12px",
                          width: "40px",
                          height: "40px",
                          borderRadius: "50%",
                          backgroundColor: `var(--${step.color})`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: `var(--${step.color}-foreground)`,
                          fontSize: "1rem",
                          fontWeight: "bold",
                          boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
                        }}
                      >
                        {step.number}
                      </div>
                      <h3
                        style={{
                          fontSize: "1.25rem",
                          fontWeight: "600",
                          marginBottom: "0.75rem",
                          color: "var(--foreground)",
                        }}
                      >
                        {step.title}
                      </h3>
                      <p
                        style={{
                          color: "var(--muted-foreground)",
                          lineHeight: "1.5",
                        }}
                      >
                        {step.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Pricing Preview */}
        <section
          id="precos"
          style={{
            padding: "5rem 1.5rem",
            backgroundColor:
              "color-mix(in oklch, var(--muted) 30%, transparent)",
          }}
        >
          <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
            <div
              style={{
                maxWidth: "768px",
                margin: "0 auto 4rem",
                textAlign: "center",
              }}
            >
              <h2
                style={{
                  fontSize: "clamp(1.875rem, 4vw, 2.25rem)",
                  fontWeight: "bold",
                  marginBottom: "1rem",
                  color: "var(--foreground)",
                }}
              >
                Preços transparentes em reais
              </h2>
              <p
                style={{
                  fontSize: "1.125rem",
                  color: "var(--muted-foreground)",
                }}
              >
                Escolha o plano ideal para suas necessidades
              </p>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "1.5rem",
                maxWidth: "1200px",
                margin: "0 auto",
              }}
            >
              {/* Free */}
              <div
                style={{
                  padding: "2rem",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                  backgroundColor: "var(--card)",
                }}
              >
                <div style={{ marginBottom: "2rem" }}>
                  <h3
                    style={{
                      fontSize: "1.125rem",
                      fontWeight: "600",
                      marginBottom: "0.5rem",
                      color: "var(--foreground)",
                    }}
                  >
                    Gratuito
                  </h3>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "baseline",
                      gap: "0.25rem",
                      marginBottom: "0.25rem",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "2.5rem",
                        fontWeight: "bold",
                        color: "var(--foreground)",
                      }}
                    >
                      R$ 0
                    </span>
                  </div>
                  <p
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    Para experimentar
                  </p>
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  {[
                    "3 análises gratuitas",
                    "Otimização básica ATS",
                    "Download em PDF",
                    "Sem cartão de crédito",
                  ].map((feature, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "0.75rem",
                        marginBottom: "0.75rem",
                      }}
                    >
                      <CheckCircle2
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "var(--primary)",
                          flexShrink: 0,
                          marginTop: "2px",
                        }}
                      />
                      <span
                        style={{
                          fontSize: "0.875rem",
                          color: "var(--foreground)",
                        }}
                      >
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  style={{
                    width: "100%",
                    height: "44px",
                    borderRadius: "8px",
                    border: "1px solid var(--border)",
                    backgroundColor: "transparent",
                    color: "var(--foreground)",
                    fontWeight: "500",
                    cursor: "pointer",
                  }}
                >
                  Começar Grátis
                </button>
              </div>

              {/* Flex 25 */}
              <div
                style={{
                  position: "relative",
                  padding: "2rem",
                  borderRadius: "16px",
                  border: "2px solid var(--primary)",
                  backgroundColor: "var(--card)",
                  boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: "-12px",
                    left: "50%",
                    transform: "translateX(-50%)",
                    padding: "0.25rem 0.75rem",
                    borderRadius: "9999px",
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                    fontSize: "0.75rem",
                    fontWeight: "bold",
                  }}
                >
                  Mais Popular
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  <h3
                    style={{
                      fontSize: "1.125rem",
                      fontWeight: "600",
                      marginBottom: "0.5rem",
                      color: "var(--foreground)",
                    }}
                  >
                    Flex 25
                  </h3>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "baseline",
                      gap: "0.25rem",
                      marginBottom: "0.25rem",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "2.5rem",
                        fontWeight: "bold",
                        color: "var(--foreground)",
                      }}
                    >
                      R$ 59,90
                    </span>
                  </div>
                  <p
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    25 créditos • R$ 2,40/análise
                  </p>
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  {[
                    "25 análises completas",
                    "Créditos nunca expiram",
                    "Download DOCX e PDF",
                    "Suporte por email",
                    "Sistema de indicações",
                  ].map((feature, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "0.75rem",
                        marginBottom: "0.75rem",
                      }}
                    >
                      <CheckCircle2
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "var(--primary)",
                          flexShrink: 0,
                          marginTop: "2px",
                        }}
                      />
                      <span
                        style={{
                          fontSize: "0.875rem",
                          color: "var(--foreground)",
                        }}
                      >
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  style={{
                    width: "100%",
                    height: "44px",
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                    borderRadius: "8px",
                    fontWeight: "600",
                    border: "none",
                    cursor: "pointer",
                    boxShadow:
                      "0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)",
                  }}
                >
                  Comprar Créditos
                </button>
              </div>

              {/* Flow Pro */}
              <div
                style={{
                  position: "relative",
                  padding: "2rem",
                  borderRadius: "16px",
                  border: "1px solid var(--border)",
                  backgroundColor: "var(--card)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: "-12px",
                    left: "50%",
                    transform: "translateX(-50%)",
                    padding: "0.25rem 0.75rem",
                    borderRadius: "9999px",
                    backgroundColor: "var(--secondary)",
                    color: "var(--secondary-foreground)",
                    fontSize: "0.75rem",
                    fontWeight: "bold",
                  }}
                >
                  Melhor Valor
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  <h3
                    style={{
                      fontSize: "1.125rem",
                      fontWeight: "600",
                      marginBottom: "0.5rem",
                      color: "var(--foreground)",
                    }}
                  >
                    Flow Pro
                  </h3>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "baseline",
                      gap: "0.25rem",
                      marginBottom: "0.25rem",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "2.5rem",
                        fontWeight: "bold",
                        color: "var(--foreground)",
                      }}
                    >
                      R$ 49,90
                    </span>
                    <span style={{ color: "var(--muted-foreground)" }}>
                      /mês
                    </span>
                  </div>
                  <p
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    60 análises mensais
                  </p>
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  {[
                    "60 análises por mês",
                    "Rollover até 30 análises",
                    "Templates de currículo",
                    "Insights de carreira",
                    "Suporte prioritário",
                    "20% off em créditos extras",
                  ].map((feature, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "0.75rem",
                        marginBottom: "0.75rem",
                      }}
                    >
                      <CheckCircle2
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "var(--primary)",
                          flexShrink: 0,
                          marginTop: "2px",
                        }}
                      />
                      <span
                        style={{
                          fontSize: "0.875rem",
                          color: "var(--foreground)",
                        }}
                      >
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  style={{
                    width: "100%",
                    height: "44px",
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                    borderRadius: "8px",
                    fontWeight: "600",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Começar Assinatura
                </button>
              </div>
            </div>

            <div style={{ textAlign: "center", marginTop: "3rem" }}>
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "1rem",
                  fontSize: "0.875rem",
                  color: "var(--muted-foreground)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <Lock style={{ width: "16px", height: "16px" }} />
                  <span>Pagamento seguro</span>
                </div>
                <span>•</span>
                <span>Cancele quando quiser</span>
                <span>•</span>
                <span>Garantia de 7 dias</span>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" style={{ padding: "5rem 1.5rem" }}>
          <div style={{ maxWidth: "768px", margin: "0 auto" }}>
            <div style={{ textAlign: "center", marginBottom: "4rem" }}>
              <h2
                style={{
                  fontSize: "clamp(1.875rem, 4vw, 2.25rem)",
                  fontWeight: "bold",
                  marginBottom: "1rem",
                  color: "var(--foreground)",
                }}
              >
                Perguntas frequentes
              </h2>
              <p
                style={{
                  fontSize: "1.125rem",
                  color: "var(--muted-foreground)",
                }}
              >
                Tire suas dúvidas sobre o CV-Match
              </p>
            </div>

            <div
              style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
            >
              {[
                {
                  q: "Como funciona a análise por IA?",
                  a: "Nossa inteligência artificial compara seu currículo com a descrição da vaga, identifica palavras-chave ausentes, problemas de formatação ATS e sugere melhorias específicas baseadas no mercado brasileiro.",
                },
                {
                  q: "Meus dados estão seguros?",
                  a: "Sim! Somos 100% compatíveis com a LGPD. Seus dados são criptografados, nunca compartilhados com terceiros, e você pode solicitar exclusão completa a qualquer momento.",
                },
                {
                  q: "Qual a diferença entre Flex e Flow?",
                  a: "Flex são créditos avulsos que nunca expiram - ideal para uso esporádico. Flow é assinatura mensal com mais análises, recursos premium e melhor custo-benefício para quem usa frequentemente.",
                },
                {
                  q: "O que são os 3 usos gratuitos?",
                  a: "Você pode fazer 3 análises completas gratuitamente, sem precisar cadastrar cartão de crédito. Depois, escolha o plano ideal para continuar.",
                },
              ].map((faq, index) => (
                <div
                  key={index}
                  style={{
                    borderRadius: "12px",
                    border: "1px solid var(--border)",
                    backgroundColor: "var(--card)",
                    overflow: "hidden",
                  }}
                >
                  <button
                    onClick={() => toggleFaq(index)}
                    style={{
                      width: "100%",
                      padding: "1rem 1.5rem",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      textAlign: "left",
                      backgroundColor: "transparent",
                      border: "none",
                      cursor: "pointer",
                    }}
                  >
                    <span
                      style={{
                        fontWeight: "500",
                        paddingRight: "1rem",
                        color: "var(--foreground)",
                      }}
                    >
                      {faq.q}
                    </span>
                    <ChevronDown
                      style={{
                        width: "20px",
                        height: "20px",
                        color: "var(--muted-foreground)",
                        flexShrink: 0,
                        transform:
                          openFaq === index ? "rotate(180deg)" : "rotate(0deg)",
                        transition: "transform 0.3s",
                      }}
                    />
                  </button>
                  {openFaq === index && (
                    <div style={{ padding: "0 1.5rem 1rem" }}>
                      <p
                        style={{
                          fontSize: "0.875rem",
                          color: "var(--muted-foreground)",
                          lineHeight: "1.5",
                        }}
                      >
                        {faq.a}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section style={{ padding: "5rem 1.5rem" }}>
          <div style={{ maxWidth: "896px", margin: "0 auto" }}>
            <div
              style={{
                position: "relative",
                borderRadius: "24px",
                border: "1px solid var(--border)",
                background:
                  "linear-gradient(135deg, color-mix(in oklch, var(--primary) 5%, transparent), color-mix(in oklch, var(--secondary) 5%, transparent), color-mix(in oklch, var(--accent) 5%, transparent))",
                padding: "3rem",
                textAlign: "center",
                overflow: "hidden",
              }}
            >
              <div style={{ position: "relative" }}>
                <h2
                  style={{
                    fontSize: "clamp(1.875rem, 4vw, 2.25rem)",
                    fontWeight: "bold",
                    marginBottom: "1.5rem",
                    color: "var(--foreground)",
                  }}
                >
                  Pronto para conquistar sua próxima oportunidade?
                </h2>
                <p
                  style={{
                    fontSize: "1.125rem",
                    color: "var(--muted-foreground)",
                    maxWidth: "672px",
                    margin: "0 auto 2rem",
                  }}
                >
                  Junte-se a milhares de profissionais brasileiros que já
                  transformaram suas carreiras
                </p>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "1rem",
                    alignItems: "center",
                  }}
                >
                  <button
                    style={{
                      width: "100%",
                      maxWidth: "300px",
                      height: "48px",
                      padding: "0 2rem",
                      backgroundColor: "var(--primary)",
                      color: "var(--primary-foreground)",
                      borderRadius: "8px",
                      fontWeight: "600",
                      border: "none",
                      cursor: "pointer",
                      boxShadow:
                        "0 10px 15px -3px color-mix(in oklch, var(--primary) 20%, transparent)",
                    }}
                  >
                    Começar Gratuitamente
                  </button>
                  <button
                    style={{
                      width: "100%",
                      maxWidth: "300px",
                      height: "48px",
                      padding: "0 2rem",
                      borderRadius: "8px",
                      fontWeight: "600",
                      border: "1px solid var(--border)",
                      backgroundColor: "transparent",
                      color: "var(--foreground)",
                      cursor: "pointer",
                    }}
                  >
                    Ver Demonstração
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer
          style={{
            borderTop: "1px solid var(--border)",
            padding: "4rem 1.5rem",
          }}
        >
          <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "3rem",
                marginBottom: "3rem",
              }}
            >
              <div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    marginBottom: "1rem",
                  }}
                >
                  <div
                    style={{
                      width: "32px",
                      height: "32px",
                      backgroundColor: "var(--primary)",
                      borderRadius: "8px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <FileCheck
                      style={{
                        width: "20px",
                        height: "20px",
                        color: "var(--primary-foreground)",
                      }}
                    />
                  </div>
                  <span
                    style={{
                      fontSize: "1.125rem",
                      fontWeight: "bold",
                      color: "var(--foreground)",
                    }}
                  >
                    CV-Match
                  </span>
                </div>
                <p
                  style={{
                    fontSize: "0.875rem",
                    color: "var(--muted-foreground)",
                    lineHeight: "1.5",
                  }}
                >
                  Otimização inteligente de currículos para o mercado brasileiro
                </p>
              </div>

              {[
                {
                  title: "Produto",
                  links: ["Como Funciona", "Preços", "Recursos", "FAQ"],
                },
                {
                  title: "Empresa",
                  links: ["Sobre", "Blog", "Contato"],
                },
                {
                  title: "Legal",
                  links: ["Privacidade", "Termos de Uso", "LGPD"],
                },
              ].map((column, idx) => (
                <div key={idx}>
                  <h4
                    style={{
                      fontWeight: "600",
                      marginBottom: "1rem",
                      fontSize: "0.875rem",
                      color: "var(--foreground)",
                    }}
                  >
                    {column.title}
                  </h4>
                  <ul
                    style={{
                      listStyle: "none",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.75rem",
                    }}
                  >
                    {column.links.map((link, linkIdx) => (
                      <li key={linkIdx}>
                        <a
                          href="#"
                          style={{
                            fontSize: "0.875rem",
                            color: "var(--muted-foreground)",
                            textDecoration: "none",
                          }}
                        >
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div
              style={{
                borderTop: "1px solid var(--border)",
                paddingTop: "2rem",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "1rem",
                fontSize: "0.875rem",
                color: "var(--muted-foreground)",
              }}
            >
              <p>© 2025 CV-Match. Todos os direitos reservados.</p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default CVMatchLanding;

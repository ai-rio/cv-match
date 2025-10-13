import React, { useState } from "react";
import {
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle2,
  ArrowLeft,
  FileText,
  AlertCircle,
} from "lucide-react";

const CVMatchAuth = () => {
  const [mode, setMode] = useState("signup");
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (mode === "signup") {
      if (!formData.name || formData.name.length < 2) {
        newErrors.name = "Nome deve ter pelo menos 2 caracteres";
      }
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = "Confirme sua senha";
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = "As senhas não coincidem";
      }
    }

    if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email inválido";
    }

    if (
      mode !== "reset" &&
      (!formData.password || formData.password.length < 6)
    ) {
      newErrors.password = "Senha deve ter pelo menos 6 caracteres";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      if (mode === "signup") {
        setMode("verify");
      } else if (mode === "reset") {
        setMode("reset-sent");
      }
    }
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
          --muted: oklch(0.8828 0.0285 98.1033);
          --muted-foreground: oklch(0.5382 0 0);
          --accent: oklch(0.8269 0.108 211.9627);
          --accent-foreground: oklch(0.3211 0 0);
          --destructive: oklch(0.6368 0.2078 25.3313);
          --border: oklch(0.8699 0 0);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        input:focus { outline: none; border-color: var(--primary); }
      `}</style>

      <div
        style={{
          minHeight: "100vh",
          backgroundColor: "var(--background)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem 1rem",
        }}
      >
        <div style={{ width: "100%", maxWidth: "440px" }}>
          {/* Logo Header */}
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div
              style={{
                width: "56px",
                height: "56px",
                backgroundColor: "var(--primary)",
                borderRadius: "12px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 1rem",
                boxShadow:
                  "0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)",
              }}
            >
              <FileText
                style={{
                  width: "32px",
                  height: "32px",
                  color: "var(--primary-foreground)",
                }}
              />
            </div>
            <h1
              style={{
                fontSize: "1.75rem",
                fontWeight: "bold",
                color: "var(--foreground)",
                marginBottom: "0.5rem",
              }}
            >
              CV-Match
            </h1>
            <p
              style={{ fontSize: "0.875rem", color: "var(--muted-foreground)" }}
            >
              {mode === "signup" && "Crie sua conta e comece grátis"}
              {mode === "login" && "Entre na sua conta"}
              {mode === "verify" && "Verifique seu email"}
              {mode === "reset" && "Recupere sua senha"}
              {mode === "reset-sent" && "Email enviado com sucesso"}
            </p>
          </div>

          {/* Sign Up */}
          {mode === "signup" && (
            <div
              style={{
                backgroundColor: "var(--card)",
                borderRadius: "16px",
                border: "1px solid var(--border)",
                padding: "2rem",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.75rem",
                  marginBottom: "1.5rem",
                }}
              >
                <button
                  style={{
                    width: "100%",
                    height: "44px",
                    backgroundColor: "var(--background)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    fontSize: "0.875rem",
                    fontWeight: "600",
                    color: "var(--foreground)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "0.75rem",
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 18 18">
                    <path
                      fill="#4285F4"
                      d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"
                    />
                    <path
                      fill="#34A853"
                      d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.593.102-1.17.282-1.709V4.958H.957C.347 6.173 0 7.548 0 9c0 1.452.348 2.827.957 4.042l3.007-2.335z"
                    />
                    <path
                      fill="#EA4335"
                      d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"
                    />
                  </svg>
                  Continuar com Google
                </button>

                <button
                  style={{
                    width: "100%",
                    height: "44px",
                    backgroundColor: "#0A66C2",
                    border: "none",
                    borderRadius: "8px",
                    fontSize: "0.875rem",
                    fontWeight: "600",
                    color: "white",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "0.75rem",
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                  </svg>
                  Continuar com LinkedIn
                </button>
              </div>

              <div
                style={{
                  position: "relative",
                  textAlign: "center",
                  margin: "1.5rem 0",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: 0,
                    right: 0,
                    height: "1px",
                    backgroundColor: "var(--border)",
                  }}
                />
                <span
                  style={{
                    position: "relative",
                    backgroundColor: "var(--card)",
                    padding: "0 1rem",
                    fontSize: "0.75rem",
                    color: "var(--muted-foreground)",
                    fontWeight: "500",
                  }}
                >
                  ou cadastre-se com email
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                }}
              >
                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "var(--foreground)",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Nome completo
                  </label>
                  <div style={{ position: "relative" }}>
                    <User
                      style={{
                        position: "absolute",
                        left: "12px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        width: "18px",
                        height: "18px",
                        color: "var(--muted-foreground)",
                      }}
                    />
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) =>
                        handleInputChange("name", e.target.value)
                      }
                      placeholder="Seu nome"
                      style={{
                        width: "100%",
                        height: "44px",
                        paddingLeft: "40px",
                        paddingRight: "12px",
                        fontSize: "0.875rem",
                        border: `1px solid ${errors.name ? "var(--destructive)" : "var(--border)"}`,
                        borderRadius: "8px",
                        backgroundColor: "var(--background)",
                        color: "var(--foreground)",
                      }}
                    />
                  </div>
                  {errors.name && (
                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--destructive)",
                        marginTop: "0.25rem",
                      }}
                    >
                      {errors.name}
                    </p>
                  )}
                </div>

                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "var(--foreground)",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Email
                  </label>
                  <div style={{ position: "relative" }}>
                    <Mail
                      style={{
                        position: "absolute",
                        left: "12px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        width: "18px",
                        height: "18px",
                        color: "var(--muted-foreground)",
                      }}
                    />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        handleInputChange("email", e.target.value)
                      }
                      placeholder="seu@email.com"
                      style={{
                        width: "100%",
                        height: "44px",
                        paddingLeft: "40px",
                        paddingRight: "12px",
                        fontSize: "0.875rem",
                        border: `1px solid ${errors.email ? "var(--destructive)" : "var(--border)"}`,
                        borderRadius: "8px",
                        backgroundColor: "var(--background)",
                        color: "var(--foreground)",
                      }}
                    />
                  </div>
                  {errors.email && (
                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--destructive)",
                        marginTop: "0.25rem",
                      }}
                    >
                      {errors.email}
                    </p>
                  )}
                </div>

                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "var(--foreground)",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Senha
                  </label>
                  <div style={{ position: "relative" }}>
                    <Lock
                      style={{
                        position: "absolute",
                        left: "12px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        width: "18px",
                        height: "18px",
                        color: "var(--muted-foreground)",
                      }}
                    />
                    <input
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={(e) =>
                        handleInputChange("password", e.target.value)
                      }
                      placeholder="Mínimo 6 caracteres"
                      style={{
                        width: "100%",
                        height: "44px",
                        paddingLeft: "40px",
                        paddingRight: "40px",
                        fontSize: "0.875rem",
                        border: `1px solid ${errors.password ? "var(--destructive)" : "var(--border)"}`,
                        borderRadius: "8px",
                        backgroundColor: "var(--background)",
                        color: "var(--foreground)",
                      }}
                    />
                    <button
                      onClick={() => setShowPassword(!showPassword)}
                      style={{
                        position: "absolute",
                        right: "12px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        backgroundColor: "transparent",
                        border: "none",
                        cursor: "pointer",
                        padding: 0,
                      }}
                    >
                      {showPassword ? (
                        <EyeOff
                          style={{
                            width: "18px",
                            height: "18px",
                            color: "var(--muted-foreground)",
                          }}
                        />
                      ) : (
                        <Eye
                          style={{
                            width: "18px",
                            height: "18px",
                            color: "var(--muted-foreground)",
                          }}
                        />
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--destructive)",
                        marginTop: "0.25rem",
                      }}
                    >
                      {errors.password}
                    </p>
                  )}
                </div>

                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "var(--foreground)",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Confirmar senha
                  </label>
                  <div style={{ position: "relative" }}>
                    <Lock
                      style={{
                        position: "absolute",
                        left: "12px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        width: "18px",
                        height: "18px",
                        color: "var(--muted-foreground)",
                      }}
                    />
                    <input
                      type={showPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={(e) =>
                        handleInputChange("confirmPassword", e.target.value)
                      }
                      placeholder="Digite a senha novamente"
                      style={{
                        width: "100%",
                        height: "44px",
                        paddingLeft: "40px",
                        paddingRight: "12px",
                        fontSize: "0.875rem",
                        border: `1px solid ${errors.confirmPassword ? "var(--destructive)" : "var(--border)"}`,
                        borderRadius: "8px",
                        backgroundColor: "var(--background)",
                        color: "var(--foreground)",
                      }}
                    />
                  </div>
                  {errors.confirmPassword && (
                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--destructive)",
                        marginTop: "0.25rem",
                      }}
                    >
                      {errors.confirmPassword}
                    </p>
                  )}
                </div>
              </div>

              <div
                style={{
                  marginTop: "1rem",
                  padding: "0.75rem",
                  backgroundColor:
                    "color-mix(in oklch, var(--muted) 50%, transparent)",
                  borderRadius: "8px",
                  fontSize: "0.75rem",
                  color: "var(--muted-foreground)",
                  lineHeight: "1.5",
                }}
              >
                Ao criar sua conta, você concorda com nossos{" "}
                <a
                  href="#"
                  style={{
                    color: "var(--primary)",
                    textDecoration: "none",
                    fontWeight: "500",
                  }}
                >
                  Termos de Uso
                </a>
                {" e "}
                <a
                  href="#"
                  style={{
                    color: "var(--primary)",
                    textDecoration: "none",
                    fontWeight: "500",
                  }}
                >
                  Política de Privacidade
                </a>
              </div>

              <button
                onClick={handleSubmit}
                style={{
                  width: "100%",
                  height: "48px",
                  marginTop: "1.5rem",
                  backgroundColor: "var(--primary)",
                  color: "var(--primary-foreground)",
                  border: "none",
                  borderRadius: "8px",
                  fontSize: "0.875rem",
                  fontWeight: "600",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem",
                  boxShadow:
                    "0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)",
                }}
              >
                Criar Conta Grátis
                <ArrowRight style={{ width: "18px", height: "18px" }} />
              </button>

              <div
                style={{
                  marginTop: "1.5rem",
                  textAlign: "center",
                  fontSize: "0.875rem",
                  color: "var(--muted-foreground)",
                }}
              >
                Já tem uma conta?{" "}
                <button
                  onClick={() => setMode("login")}
                  style={{
                    backgroundColor: "transparent",
                    border: "none",
                    color: "var(--primary)",
                    fontWeight: "600",
                    cursor: "pointer",
                    fontSize: "0.875rem",
                  }}
                >
                  Fazer login
                </button>
              </div>
            </div>
          )}

          {/* Login - simplified version */}
          {mode === "login" && (
            <div
              style={{
                backgroundColor: "var(--card)",
                borderRadius: "16px",
                border: "1px solid var(--border)",
                padding: "2rem",
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                  marginBottom: "1.5rem",
                }}
              >
                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "var(--foreground)",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Email
                  </label>
                  <input
                    type="email"
                    placeholder="seu@email.com"
                    style={{
                      width: "100%",
                      height: "44px",
                      padding: "0 12px",
                      fontSize: "0.875rem",
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      backgroundColor: "var(--background)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>
                <div>
                  <label
                    style={{
                      display: "block",
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "var(--foreground)",
                      marginBottom: "0.5rem",
                    }}
                  >
                    Senha
                  </label>
                  <input
                    type="password"
                    placeholder="Sua senha"
                    style={{
                      width: "100%",
                      height: "44px",
                      padding: "0 12px",
                      fontSize: "0.875rem",
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      backgroundColor: "var(--background)",
                      color: "var(--foreground)",
                    }}
                  />
                </div>
              </div>
              <button
                style={{
                  width: "100%",
                  height: "48px",
                  backgroundColor: "var(--primary)",
                  color: "var(--primary-foreground)",
                  border: "none",
                  borderRadius: "8px",
                  fontSize: "0.875rem",
                  fontWeight: "600",
                  cursor: "pointer",
                }}
              >
                Entrar
              </button>
              <div
                style={{
                  marginTop: "1.5rem",
                  textAlign: "center",
                  fontSize: "0.875rem",
                  color: "var(--muted-foreground)",
                }}
              >
                Não tem conta?{" "}
                <button
                  onClick={() => setMode("signup")}
                  style={{
                    backgroundColor: "transparent",
                    border: "none",
                    color: "var(--primary)",
                    fontWeight: "600",
                    cursor: "pointer",
                  }}
                >
                  Criar conta
                </button>
              </div>
            </div>
          )}

          {/* Email Verification */}
          {mode === "verify" && (
            <div
              style={{
                backgroundColor: "var(--card)",
                borderRadius: "16px",
                border: "1px solid var(--border)",
                padding: "3rem 2rem",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  width: "80px",
                  height: "80px",
                  margin: "0 auto 2rem",
                  backgroundColor:
                    "color-mix(in oklch, var(--primary) 10%, transparent)",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Mail
                  style={{
                    width: "40px",
                    height: "40px",
                    color: "var(--primary)",
                  }}
                />
              </div>
              <h2
                style={{
                  fontSize: "1.5rem",
                  fontWeight: "bold",
                  color: "var(--foreground)",
                  marginBottom: "1rem",
                }}
              >
                Verifique seu email
              </h2>
              <p
                style={{
                  fontSize: "0.875rem",
                  color: "var(--muted-foreground)",
                  marginBottom: "2rem",
                }}
              >
                Enviamos um link para <strong>{formData.email}</strong>. Clique
                para ativar sua conta.
              </p>
              <button
                onClick={() => setMode("login")}
                style={{
                  width: "100%",
                  height: "44px",
                  backgroundColor: "transparent",
                  color: "var(--muted-foreground)",
                  border: "none",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem",
                }}
              >
                <ArrowLeft style={{ width: "16px", height: "16px" }} />
                Voltar ao login
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CVMatchAuth;

import React, { useState } from 'react';
import { Plus, FileText, TrendingUp, Award, Settings, CreditCard, Gift, LogOut, Menu, X, ChevronRight, Download, Eye, Calendar, Sparkles, Zap, Target } from 'lucide-react';

const CVMatchDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Mock user data
  const user = {
    name: 'Maria Silva',
    email: 'maria.silva@email.com',
    plan: 'Flex', // or 'Flow Pro'
    credits: 18,
    monthlyLimit: null, // 60 for Flow users
    usedThisMonth: 0
  };

  // Mock analysis history
  const recentAnalyses = [
    {
      id: 1,
      jobTitle: 'Desenvolvedor Full Stack',
      company: 'Tech Solutions',
      score: 92,
      date: '2025-10-07',
      status: 'completed'
    },
    {
      id: 2,
      jobTitle: 'Engenheiro de Software Senior',
      company: 'StartupXYZ',
      score: 85,
      date: '2025-10-05',
      status: 'completed'
    },
    {
      id: 3,
      jobTitle: 'Tech Lead',
      company: 'Empresa ABC',
      score: 78,
      date: '2025-10-03',
      status: 'completed'
    }
  ];

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

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        
        @media (min-width: 768px) {
          .md-flex { display: flex !important; }
          .md-hidden { display: none !important; }
        }
      `}</style>

      <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--background)' }}>
        {/* Sidebar - Desktop */}
        <aside style={{
          display: 'none',
          width: '280px',
          backgroundColor: 'var(--card)',
          borderRight: '1px solid var(--border)',
          flexDirection: 'column',
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0
        }} className="md-flex">
          <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{
                width: '32px',
                height: '32px',
                backgroundColor: 'var(--primary)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <FileText style={{ width: '20px', height: '20px', color: 'var(--primary-foreground)' }} />
              </div>
              <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--foreground)' }}>CV-Match</span>
            </div>
          </div>

          <nav style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <button style={{
                width: '100%',
                height: '44px',
                backgroundColor: 'var(--primary)',
                color: 'var(--primary-foreground)',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '0.875rem',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)'
              }}>
                <Plus style={{ width: '18px', height: '18px' }} />
                Nova Análise
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {[
                { icon: TrendingUp, label: 'Dashboard', active: true },
                { icon: FileText, label: 'Minhas Análises', active: false },
                { icon: Gift, label: 'Indicações', active: false },
                { icon: Award, label: 'Planos', active: false }
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button key={idx} style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    backgroundColor: item.active ? 'color-mix(in oklch, var(--primary) 10%, transparent)' : 'transparent',
                    color: item.active ? 'var(--primary)' : 'var(--muted-foreground)',
                    borderRadius: '8px',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    fontSize: '0.875rem',
                    fontWeight: item.active ? '600' : '500',
                    textAlign: 'left',
                    transition: 'all 0.2s'
                  }}>
                    <Icon style={{ width: '18px', height: '18px' }} />
                    {item.label}
                  </button>
                );
              })}
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {[
                  { icon: Settings, label: 'Configurações' },
                  { icon: CreditCard, label: 'Billing' },
                  { icon: LogOut, label: 'Sair' }
                ].map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <button key={idx} style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      backgroundColor: 'transparent',
                      color: 'var(--muted-foreground)',
                      borderRadius: '8px',
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      textAlign: 'left'
                    }}>
                      <Icon style={{ width: '18px', height: '18px' }} />
                      {item.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </nav>
        </aside>

        {/* Sidebar - Mobile */}
        {sidebarOpen && (
          <div style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 40
          }} onClick={() => setSidebarOpen(false)}>
            <aside style={{
              width: '280px',
              height: '100vh',
              backgroundColor: 'var(--card)',
              display: 'flex',
              flexDirection: 'column',
              position: 'fixed',
              left: 0,
              top: 0,
              zIndex: 50
            }} onClick={(e) => e.stopPropagation()}>
              <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    backgroundColor: 'var(--primary)',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <FileText style={{ width: '20px', height: '20px', color: 'var(--primary-foreground)' }} />
                  </div>
                  <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--foreground)' }}>CV-Match</span>
                </div>
                <button onClick={() => setSidebarOpen(false)} style={{
                  width: '32px',
                  height: '32px',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <X style={{ width: '20px', height: '20px', color: 'var(--foreground)' }} />
                </button>
              </div>

              <nav style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
                {/* Same nav content as desktop */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <button style={{
                    width: '100%',
                    height: '44px',
                    backgroundColor: 'var(--primary)',
                    color: 'var(--primary-foreground)',
                    borderRadius: '8px',
                    fontWeight: '600',
                    fontSize: '0.875rem',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}>
                    <Plus style={{ width: '18px', height: '18px' }} />
                    Nova Análise
                  </button>
                </div>
              </nav>
            </aside>
          </div>
        )}

        {/* Main Content */}
        <main style={{
          flex: 1,
          marginLeft: '0',
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh'
        }} className="md-ml-280">
          {/* Top Bar */}
          <header style={{
            height: '64px',
            backgroundColor: 'var(--card)',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 1.5rem',
            position: 'sticky',
            top: 0,
            zIndex: 30
          }}>
            <button onClick={() => setSidebarOpen(true)} style={{
              width: '40px',
              height: '40px',
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }} className="md-hidden">
              <Menu style={{ width: '24px', height: '24px', color: 'var(--foreground)' }} />
            </button>

            <div style={{ display: 'none', alignItems: 'center', gap: '0.5rem' }} className="md-flex">
              <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--foreground)' }}>Dashboard</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{
                height: '40px',
                padding: '0 1rem',
                backgroundColor: 'color-mix(in oklch, var(--primary) 10%, transparent)',
                color: 'var(--primary)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '600'
              }}>
                <Sparkles style={{ width: '16px', height: '16px' }} />
                <span>{user.credits} créditos</span>
              </div>

              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: 'color-mix(in oklch, var(--primary) 20%, transparent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary)',
                fontWeight: 'bold',
                fontSize: '0.875rem'
              }}>
                {user.name.split(' ').map(n => n[0]).join('')}
              </div>
            </div>
          </header>

          {/* Dashboard Content */}
          <div style={{ flex: 1, padding: '2rem 1.5rem', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
            {/* Welcome Section */}
            <div style={{ marginBottom: '2rem' }}>
              <h1 style={{ fontSize: 'clamp(1.5rem, 3vw, 2rem)', fontWeight: 'bold', color: 'var(--foreground)', marginBottom: '0.5rem' }}>
                Olá, {user.name.split(' ')[0]}! 👋
              </h1>
              <p style={{ fontSize: '1rem', color: 'var(--muted-foreground)' }}>
                Pronto para otimizar mais currículos hoje?
              </p>
            </div>

            {/* Stats Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              {/* Credits Card */}
              <div style={{
                padding: '1.5rem',
                backgroundColor: 'var(--card)',
                borderRadius: '16px',
                border: '1px solid var(--border)',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-20px',
                  right: '-20px',
                  width: '100px',
                  height: '100px',
                  background: 'radial-gradient(circle, color-mix(in oklch, var(--primary) 15%, transparent) 0%, transparent 70%)'
                }} />
                <div style={{ position: 'relative' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      backgroundColor: 'color-mix(in oklch, var(--primary) 10%, transparent)',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Sparkles style={{ width: '20px', height: '20px', color: 'var(--primary)' }} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', fontWeight: '500' }}>
                        Créditos Disponíveis
                      </div>
                      <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'var(--foreground)' }}>
                        {user.credits}
                      </div>
                    </div>
                  </div>
                  <button style={{
                    width: '100%',
                    height: '36px',
                    backgroundColor: 'transparent',
                    color: 'var(--primary)',
                    border: '1px solid var(--primary)',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}>
                    <Plus style={{ width: '16px', height: '16px' }} />
                    Comprar Mais
                  </button>
                </div>
              </div>

              {/* Total Analyses */}
              <div style={{
                padding: '1.5rem',
                backgroundColor: 'var(--card)',
                borderRadius: '16px',
                border: '1px solid var(--border)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    backgroundColor: 'color-mix(in oklch, var(--secondary) 10%, transparent)',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Target style={{ width: '20px', height: '20px', color: 'var(--secondary)' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', fontWeight: '500' }}>
                      Análises Feitas
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'var(--foreground)' }}>
                      {recentAnalyses.length}
                    </div>
                  </div>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>
                  Total de currículos otimizados
                </div>
              </div>

              {/* Average Score */}
              <div style={{
                padding: '1.5rem',
                backgroundColor: 'var(--card)',
                borderRadius: '16px',
                border: '1px solid var(--border)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    backgroundColor: 'color-mix(in oklch, var(--accent) 10%, transparent)',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Award style={{ width: '20px', height: '20px', color: 'var(--accent-foreground)' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', fontWeight: '500' }}>
                      Score Médio
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'var(--foreground)' }}>
                      85
                    </div>
                  </div>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>
                  Compatibilidade ATS média
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div style={{
              padding: '2rem',
              backgroundColor: 'linear-gradient(135deg, color-mix(in oklch, var(--primary) 5%, transparent), color-mix(in oklch, var(--secondary) 5%, transparent))',
              borderRadius: '16px',
              border: '1px solid var(--border)',
              marginBottom: '2rem',
              textAlign: 'center'
            }}>
              <Zap style={{ width: '48px', height: '48px', color: 'var(--primary)', margin: '0 auto 1rem' }} />
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--foreground)', marginBottom: '0.5rem' }}>
                Pronto para sua próxima análise?
              </h2>
              <p style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)', marginBottom: '1.5rem' }}>
                Upload seu currículo e a descrição da vaga em segundos
              </p>
              <button style={{
                height: '48px',
                padding: '0 2rem',
                backgroundColor: 'var(--primary)',
                color: 'var(--primary-foreground)',
                borderRadius: '8px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 6px color-mix(in oklch, var(--primary) 20%, transparent)'
              }}>
                <Plus style={{ width: '20px', height: '20px' }} />
                Nova Análise
              </button>
            </div>

            {/* Recent Analyses */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--foreground)' }}>
                  Análises Recentes
                </h2>
                <button style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  color: 'var(--primary)',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '600'
                }}>
                  Ver Todas
                  <ChevronRight style={{ width: '16px', height: '16px' }} />
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {recentAnalyses.map((analysis) => (
                  <div key={analysis.id} style={{
                    padding: '1.5rem',
                    backgroundColor: 'var(--card)',
                    borderRadius: '12px',
                    border: '1px solid var(--border)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                      <div style={{ flex: 1 }}>
                        <h3 style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--foreground)', marginBottom: '0.25rem' }}>
                          {analysis.jobTitle}
                        </h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)' }}>
                          {analysis.company}
                        </p>
                      </div>
                      <div style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: analysis.score >= 90 ? 'color-mix(in oklch, var(--primary) 10%, transparent)' : 
                                       analysis.score >= 80 ? 'color-mix(in oklch, var(--secondary) 10%, transparent)' :
                                       'color-mix(in oklch, var(--accent) 10%, transparent)',
                        color: analysis.score >= 90 ? 'var(--primary)' : 
                               analysis.score >= 80 ? 'var(--secondary)' :
                               'var(--accent-foreground)',
                        borderRadius: '8px',
                        fontWeight: 'bold',
                        fontSize: '1.125rem'
                      }}>
                        {analysis.score}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>
                        <Calendar style={{ width: '14px', height: '14px' }} />
                        {new Date(analysis.date).toLocaleDateString('pt-BR')}
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button style={{
                          height: '32px',
                          padding: '0 1rem',
                          backgroundColor: 'transparent',
                          color: 'var(--primary)',
                          border: '1px solid var(--primary)',
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}>
                          <Eye style={{ width: '14px', height: '14px' }} />
                          Ver
                        </button>
                        <button style={{
                          height: '32px',
                          padding: '0 1rem',
                          backgroundColor: 'var(--primary)',
                          color: 'var(--primary-foreground)',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}>
                          <Download style={{ width: '14px', height: '14px' }} />
                          Baixar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Referral Banner */}
            <div style={{
              marginTop: '2rem',
              padding: '2rem',
              backgroundColor: 'var(--card)',
              borderRadius: '16px',
              border: '2px dashed var(--border)',
              textAlign: 'center'
            }}>
              <Gift style={{ width: '48px', height: '48px', color: 'var(--secondary)', margin: '0 auto 1rem' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--foreground)', marginBottom: '0.5rem' }}>
                Ganhe créditos grátis!
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)', marginBottom: '1.5rem', maxWidth: '400px', margin: '0 auto 1.5rem' }}>
                Indique amigos e ganhe 5 créditos para cada indicação que fizer uma análise
              </p>
              <button style={{
                height: '40px',
                padding: '0 1.5rem',
                backgroundColor: 'transparent',
                color: 'var(--secondary)',
                border: '1px solid var(--secondary)',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '0.875rem',
                cursor: 'pointer'
              }}>
                Ver Meu Código
              </button>
            </div>
          </div>
        </main>
      </div>
    </>
  );
};

export default CVMatchDashboard;
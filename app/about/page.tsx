"use client";

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section - Dramatic Brand Colors */}
      <section className="relative min-h-[80vh] bg-gradient-to-br from-[var(--bb-mahogany)] via-[var(--bb-black-bean)] to-[var(--bb-mahogany)]/90 text-white overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-[var(--bb-citron)] rounded-full blur-3xl transform translate-x-32 -translate-y-32"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-[var(--bb-champagne)] rounded-full blur-2xl transform -translate-x-16 translate-y-16"></div>
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-32 flex items-center min-h-[80vh]">
          <div className="max-w-4xl mx-auto text-center space-y-12">
            <p className="text-[var(--bb-citron)] text-sm font-medium uppercase tracking-[0.2em] opacity-90">Our Story</p>
            <h1 className="text-6xl md:text-7xl font-light leading-[0.95] text-white" style={{ fontFamily: 'Prata, Georgia, serif' }}>
              Better <span className="text-[var(--bb-citron)]">Being</span>
            </h1>
            <div className="w-24 h-px bg-gradient-to-r from-[var(--bb-citron)] to-transparent mx-auto"></div>
            <p className="text-xl leading-relaxed text-[var(--bb-champagne)] max-w-3xl mx-auto font-light">
              A creator-led wellness house rooted in slow, intimate stories and uncomplicated products that work. 
              We believe in the power of natural ingredients and thoughtful curation.
            </p>
          </div>
        </div>
        
        {/* Header needs padding for absolute positioning */}
        <div className="h-20"></div>
      </section>

      {/* Story Section - Citron Background with Brand Imagery */}
      <section className="py-32 bg-[var(--bb-citron)]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-24 items-center">
            <div className="space-y-8">
              <div className="space-y-6">
                <p className="text-[var(--bb-black-bean)] text-sm font-medium uppercase tracking-[0.2em] opacity-80">Philosophy</p>
                <h2 className="text-5xl font-light text-[var(--bb-black-bean)] leading-tight" style={{ fontFamily: 'Prata, Georgia, serif' }}>
                  Rituals for a <em className="text-[var(--bb-mahogany)]">Life Well Lived</em>
                </h2>
                <div className="w-16 h-px bg-[var(--bb-mahogany)]"></div>
                <div className="space-y-6 text-lg leading-relaxed text-[var(--bb-black-bean)] font-light">
                  <p>
                    Better Being was born from a simple belief: wellness shouldn't be complicated. 
                    In a world of endless supplements and complex regimens, we chose a different path.
                  </p>
                  <p>
                    We curate products that work—adaptogenic herbs for stress, mineral-rich superfoods 
                    for vitality, and plant medicines for deeper rest. Each product tells a story of 
                    careful sourcing, traditional wisdom, and modern understanding.
                  </p>
                  <p>
                    This is wellness without the noise. Products with purpose. Rituals that ground you.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="aspect-[4/5] relative overflow-hidden">
              <img 
                src="/assets_task_01jyyj4jt3e9atxgmk5jjt6s6n_1751224862_img_0.webp"
                alt="Natural wellness - water droplet on leaf"
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/assets_task_01k3pzrsb6fjmt46d7c18qp9zt_1756339480_img_0.webp';
                }}
              />
              
              {/* Gradient Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-[var(--bb-mahogany)]/40 to-transparent"></div>
              
              {/* Floating Badge */}
              <div className="absolute bottom-6 left-6 bg-[var(--bb-champagne)] text-[var(--bb-black-bean)] px-4 py-2 text-sm uppercase tracking-wider font-medium">
                Natural Wellness
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section - Champagne Background with Individual Color Cards */}
      <section className="py-32 bg-[var(--bb-champagne)]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <p className="text-[var(--bb-payne-gray)] text-sm font-medium uppercase tracking-[0.2em] mb-6">Our Commitment</p>
            <h2 className="text-4xl md:text-5xl font-light text-[var(--bb-black-bean)] max-w-2xl mx-auto leading-tight" style={{ fontFamily: 'Prata, Georgia, serif' }}>
              What We <em className="text-[var(--bb-mahogany)]">Stand For</em>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: "🌱",
                title: "Thoughtfully Sourced",
                description: "Every ingredient is carefully selected from ethical suppliers who share our values.",
                bgColor: "bg-[var(--bb-mahogany)]",
                textColor: "text-white",
                accentColor: "text-[var(--bb-citron)]"
              },
              {
                icon: "🔬",
                title: "Science-Backed", 
                description: "Traditional wisdom meets modern research. We choose what works, backed by evidence.",
                bgColor: "bg-[var(--bb-black-bean)]",
                textColor: "text-white",
                accentColor: "text-[var(--bb-champagne)]"
              },
              {
                icon: "🏔️",
                title: "Pure & Potent",
                description: "No fillers, no shortcuts. Just pure, potent ingredients at therapeutic dosages.",
                bgColor: "bg-[var(--bb-citron)]",
                textColor: "text-[var(--bb-black-bean)]",
                accentColor: "text-[var(--bb-mahogany)]"
              },
              {
                icon: "📖",
                title: "Story-Driven",
                description: "Each product has a story. We share the journey from source to shelf transparently.",
                bgColor: "bg-[var(--bb-payne-gray)]",
                textColor: "text-white",
                accentColor: "text-[var(--bb-citron)]"
              }
            ].map((value, index) => (
              <div key={index} className={`${value.bgColor} p-8 group hover:scale-105 transition-all duration-500 relative overflow-hidden`}>
                {/* Subtle gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                <div className="relative z-10 text-center space-y-6">
                  <div className="w-16 h-16 mx-auto bg-white/10 group-hover:bg-white/20 rounded-full flex items-center justify-center transition-all duration-300">
                    <span className="text-3xl">{value.icon}</span>
                  </div>
                  <div className="space-y-4">
                    <h3 className={`text-xl font-light ${value.textColor} group-hover:${value.accentColor} transition-colors duration-300`} style={{ fontFamily: 'Prata, Georgia, serif' }}>
                      {value.title}
                    </h3>
                    <p className={`${value.textColor} opacity-90 leading-relaxed text-sm`}>
                      {value.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Creator Section - Split Background with Payne Gray */}
      <section className="py-0">
        <div className="grid lg:grid-cols-2 min-h-[70vh]">
          {/* Image Side with Payne Gray */}
          <div className="bg-[var(--bb-payne-gray)] relative overflow-hidden flex items-center justify-center">
            <img 
              src="/assets_task_01k41a33mcfmnbrtp0g4gzy59e_1756685796_img_0.webp"
              alt="Tree of life - Better Being wellness philosophy"
              className="w-full h-full object-cover"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = '/assets_task_01k3pzrsb6fjmt46d7c18qp9zt_1756339480_img_0.webp';
              }}
            />
            
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--bb-black-bean)]/30 to-[var(--bb-mahogany)]/20"></div>
            
            {/* Badge */}
            <div className="absolute top-8 left-8 bg-[var(--bb-citron)] text-[var(--bb-black-bean)] px-4 py-2 text-sm uppercase tracking-wider font-medium">
              Creator-Led Approach
            </div>
          </div>

          {/* Content Side with Mahogany Background */}
          <div className="bg-gradient-to-br from-[var(--bb-mahogany)] to-[var(--bb-black-bean)] flex items-center text-white">
            <div className="p-16 space-y-10 max-w-lg">
              <div className="space-y-8">
                <p className="text-[var(--bb-citron)] text-sm font-medium uppercase tracking-[0.2em] opacity-90">Creator-Led</p>
                <h2 className="text-5xl font-light leading-tight" style={{ fontFamily: 'Prata, Georgia, serif' }}>
                  Personal <em className="text-[var(--bb-citron)]">Curation</em>
                </h2>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-px bg-[var(--bb-citron)]"></div>
                  <div className="w-12 h-px bg-[var(--bb-champagne)]"></div>
                </div>
                <div className="space-y-6 text-lg leading-relaxed text-[var(--bb-champagne)] font-light">
                  <p>
                    Better Being isn't just a brand—it's a personal practice shared. Every product 
                    we offer is something we use ourselves, test thoroughly, and believe in completely.
                  </p>
                  <p>
                    This isn't mass-market wellness. It's intimate curation by people who understand 
                    that true wellness is deeply personal and requires products that actually work.
                  </p>
                </div>
              </div>
              <div className="pt-6">
                <a href="/contact" className="bg-[var(--bb-citron)] hover:bg-[var(--bb-citron)]/90 text-[var(--bb-black-bean)] px-10 py-4 font-medium uppercase tracking-wider transition-all duration-300 hover:transform hover:scale-105">
                  Connect With Us
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

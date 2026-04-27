# WhatsApp AI Bot

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://www.whatsapp.com/)

**Chatbot inteligente para WhatsApp com IA, RAG e fácil deploy via Docker**

[Recursos](#-recursos) • [Pré-requisitos](#-pré-requisitos) • [Instalação](#-instalação) • [Configuração](#-configuração) • [Uso](#-uso)

</div>

---

##  Sobre o Projeto

Este é um chatbot profissional para WhatsApp que utiliza Inteligência Artificial para automatizar atendimentos, responder dúvidas e buscar informações em documentos personalizados. Perfeito para empresas que desejam oferecer suporte 24/7 de forma inteligente e escalável.

### Casos de Uso

- **Atendimento ao Cliente** - Responda perguntas frequentes automaticamente
- **Suporte Técnico** - Forneça soluções baseadas na sua base de conhecimento
- **Vendas** - Qualifique leads e tire dúvidas sobre produtos
- **RH** - Responda perguntas sobre processos seletivos e benefícios
- **Educação** - Tire dúvidas de alunos sobre materiais de estudo

---

##  Recursos

| Recurso | Descrição |
|---------|-----------|
|  **IA Inteligente** | Utiliza GPT-4/GPT-3.5 para respostas contextuais e naturais |
|  **RAG (Retrieval-Augmented Generation)** | Busca informações em seus documentos (PDF, TXT, DOCX) |
|  **Alta Performance** | FastAPI assíncrona com suporte a alta concorrência |
|  **Deploy Simplificado** | Ambiente completo com Docker Compose (um comando) |
|  **Altamente Customizável** | Prompts ajustáveis via arquivo `.env` |
|  **Seguro** | Autenticação API key e webhooks validados |
|  **Logs Detalhados** | Monitoramento completo das interações |
| **Auto-reconexão** | Reconecta automaticamente ao WhatsApp |

---

##  Tecnologias

- **[EvolutionAPI](https://doc.evolution-api.com/)** - Bridge robusta para WhatsApp Web
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web assíncrono moderno
- **[LangChain](https://www.langchain.com/)** - Orquestração de fluxos de IA
- **[OpenAI](https://platform.openai.com/)** - Modelos GPT para processamento de linguagem
- **[ChromaDB](https://www.trychroma.com/)** - Banco vetorial para busca semântica
- **[Docker](https://www.docker.com/)** - Containerização e orquestração

---

##  Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [Docker](https://docs.docker.com/get-docker/) (>= 20.10.0)
- [Docker Compose](https://docs.docker.com/compose/install/) (>= 2.0.0)
- [Git](https://git-scm.com/downloads) (para clonar o repositório)
- Conta na [OpenAI](https://platform.openai.com/) com créditos
- Número de WhatsApp válido

---




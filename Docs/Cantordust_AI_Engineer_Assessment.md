# Cantordust Analytics Pvt. Ltd.[cite: 5]
## AI Engineer Assessment — Trainee / Junior Track[cite: 5]

* **Location:** Kathmandu[cite: 5]
* **Open to:** final-year students, recent graduates, interns, trainees, and engineers with up to 1 year of experience.[cite: 5]
* **Time allowed:** 48 hours from the time you receive this brief.[cite: 5]
* **Questions:** Not answered by email. If something is genuinely ambiguous, make a reasonable assumption and write it down in your README — we read those. If you need to reach us directly, you may message Diwas Kunwar on LinkedIn: linkedin.com/in/diwas-kunwar[cite: 5]
* **Scope:** Choose exactly one task. Do not submit both.[cite: 5]
* **Contact:** info@cantor-dust.com (queries only — final submission is done through the official application form, not by email)[cite: 5]

---

## Overview[cite: 5]

Both tasks involve SunBridge Trading, a fictional Kathmandu importer bringing grid-tied solar inverters in from a manufacturer in China. Your job in both cases has the same shape: pull facts out of messy source documents using an AI pipeline, and produce a clean, honest draft SunBridge can hand to its import agent.[cite: 5]

The two tasks differ in what makes them hard.[cite: 5]

| Feature | Task 1 — Documents in hand | Task 2 — Almost nothing in hand |
| :--- | :--- | :--- |
| **Import country** | Nepal[cite: 5] | Bangladesh[cite: 5] |
| **What you get** | Two manufacturer datasheets (PDF)[cite: 5] | One datasheet (PDF), a buyer form, and call notes[cite: 5] |
| **The hard part** | The two documents don't fully agree, and the tables are hard to parse[cite: 5] | Half the information doesn't exist yet — you have to say so clearly[cite: 5] |
| **Pick this if** | You'd rather reconcile conflicting sources[cite: 5] | You'd rather handle gaps and uncertainty[cite: 5] |

All source documents are public links. Nothing is emailed to you and nothing is attached — fetching them is part of the task.[cite: 5]

You do not need to be a solar or electronics expert. You are not marked on domain knowledge.[cite: 5]

---

## How to build this[cite: 5]

Use an autonomous agent to do the work — something like LangGraph, LangChain, CrewAI, Hermes, or a similar agent framework that can fetch, read, and reason over the source documents on its own, rather than an IDE assistant you drive step by step. Beyond that, how you architect it is up to you; we're not prescribing a pipeline. Figure out what "correctly done" looks like from the brief and the checklist below.[cite: 5]

> **Not acceptable:** opening the PDFs yourself and hardcoding the values into a template. If it wouldn't survive a different revision of the same datasheet, it isn't a real pipeline.[cite: 5]

---

## The import-side checklist[cite: 5]

Real import reviews follow published national guidelines. For this exercise you do not need to find or read them. Use this generic checklist as your rough picture of what any import agent will ask about:[cite: 5]

1. **Product identity** — model number, variant, rated power, key electrical specs.[cite: 5]
2. **Manufacturer identity** — legal company name, factory address, country of manufacture.[cite: 5]
3. **Test evidence** — which standards the product claims compliance with, and whether there is anything in writing.[cite: 5]
4. **Labeling** — what the product label should carry: model, ratings, manufacturer, origin, protection rating.[cite: 5]
5. **Importer paperwork** — what SunBridge itself still has to supply or chase.[cite: 5]

Cover what is on this list, but don't treat it as a form to fill in section by section. If a section of your output is empty, say why rather than deleting it.[cite: 5]

---

## Task 1 — China → Nepal[cite: 5]

### Situation[cite: 5]
The factory has sent two datasheets. They cover the same product family but appear to be different variants and different revisions. They don't line up cleanly — some fields are named differently, some appear in only one document, and at least one value looks internally inconsistent.[cite: 5]

### Client brief[cite: 5]

> **From:** Ramesh | SunBridge Trading | Kathmandu[cite: 5]  
> **Subject:** Nepal shipment paperwork — need help[cite: 5]  
> 
> Hi,[cite: 5]  
> We're importing grid-tied inverters from China into Nepal. Our local agent keeps asking for the compliance file, and the paperwork the factory uses at home isn't the same thing.[cite: 5]  
> The manufacturer pointed us at two of their datasheets instead of sending a proper document pack. They might be for slightly different variants — we're not sure. Some numbers appear in both, sometimes worded differently, and I think one or two things are only in one of them.[cite: 5]  
> We need something we can share with the agent: what the product is, who makes it, what testing or standards are claimed, and what the label should say. If the two sources don't match, show that honestly — don't pick one and hide the other. A rough draft is fine.[cite: 5]  
> Send back whatever you think we should hand over, plus a short note on how you put it together.[cite: 5]  
> Thanks, Ramesh[cite: 5]

### Source documents[cite: 5]

* **Source 1 — manufacturer datasheet, AM2-P1 variant:** `https://www.deyeinverter.com/deyeinverter/2023/10/07/datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf`[cite: 5]
* **Source 2 — manufacturer datasheet, AM2 variant:** `https://www.deyeinverter.com/deyeinverter/2024/03/20/datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf`[cite: 5]

Pull the actual data from both. Don't take our word for what's in them.[cite: 5]

Assume SunBridge is ordering the **5 kW model**. Your draft should be about that model specifically, drawing on whatever each document says about it.[cite: 5]

### Your submission should make it easy to see[cite: 5]
* What product and variant each document appears to describe.[cite: 5]
* Field by field for the 5 kW model: what agrees across both sources, what conflicts, and what appears in only one.[cite: 5]
* Which items look relevant to an import review, and what is still unclear.[cite: 5]
* Where your pipeline was unsure of a value because of the document layout — flag it rather than guessing silently.[cite: 5]

---

## Task 2 — China → Bangladesh[cite: 5]

### Situation[cite: 5]
The factory hasn't sent real paperwork. SunBridge wants something presentable to circulate internally in the meantime. Being explicit about what's missing is the point of the exercise.[cite: 5]

### Client brief[cite: 5]

> **From:** Ramesh | SunBridge Trading | Kathmandu[cite: 5]  
> **Subject:** Bangladesh order — early draft before the factory sends the rest[cite: 5]  
> 
> Hi,[cite: 5]  
> We're importing grid-tied inverters from China into Bangladesh. The agent wants a compliance bundle but the factory hasn't sent the full set.[cite: 5]  
> Right now we only have the datasheet link, the buyer form, and my call notes below. That's genuinely everything.[cite: 5]  
> Put together something presentable — product, manufacturer, testing, labeling — and tell us plainly what we still need to chase from the factory. Mark anything unverified as "pending from manufacturer." That's a valid answer, not a failure.[cite: 5]  
> The form, my notes, and the datasheet don't fully agree on a couple of things. You don't need to decide who's right — just show all sides.[cite: 5]  
> Thanks, Ramesh[cite: 5]

### Source documents[cite: 5]

#### Source 1 — manufacturer datasheet[cite: 5]
`https://www.deyeinverter.com/deyeinverter/2023/10/07/datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf`[cite: 5]

#### Source 2 — buyer form[cite: 5]

| Field | Details |
| :--- | :--- |
| **Ref** | INT-2024-8841[cite: 5] |
| **Buyer** | SunBridge Trading Pvt. Ltd.[cite: 5] |
| **Destination** | Bangladesh[cite: 5] |
| **Item** | SUN-5K-G06P3-EU-AM2-P1 — buyer wrote "5000 W", rooftop[cite: 5] |
| **Maker** | Ningbo Deye Inverter Technology Co., Ltd., China[cite: 5] |
| **Attached docs** | none[cite: 5] |
| **Need by** | 2024-11-30[cite: 5] |

#### Source 3 — call notes from Ramesh, 2024-10-03[cite: 5]
Model SUN-5K-G06P3, 5 kW, Deye (China). Said IP65. Weight maybe 18 kg? Installer guessed. Mentioned SGS and "high 90s efficiency" on the phone — nothing in writing. No label photo yet. They want something to circulate internally before the real certificates arrive. OK to mark parts as "pending from factory" where unsure.[cite: 5]

Use only these three as source data.[cite: 5]

### Your submission should make it easy to see[cite: 5]
* What is actually established by the datasheet.[cite: 5]
* What is only stated verbally in the call notes, and where the three sources disagree.[cite: 5]
* What is pending from the factory — especially test evidence, certificates, and label photos.[cite: 5]
* A concrete list of questions SunBridge should send the factory.[cite: 5]

---

## What to submit[cite: 5]

This document describes the task only. Your finished work is not emailed or attached here — you submit it through the official Cantordust application form, along with the links below.[cite: 5]

### 1. GitHub repository[cite: 5]
* **Public:** submit the URL.[cite: 5]
* **Private:** submit the URL and invite `diwaskunwar`.[cite: 5]

**Your repo must contain:**

| Requirement | Description |
| :--- | :--- |
| **Runnable code** | Someone else can clone it, follow the README, and run your pipeline end to end from the links above.[cite: 5] |
| **README** | How to run it; which extraction/OCR approach you chose and why; how your pipeline is structured; your assumptions; what you'd do with more time.[cite: 5] |
| **Structured output** | The extracted fields as machine-readable data (JSON or similar), with source attribution per field — we want to see which document each value came from, and where confidence was low.[cite: 5] |
| **Human-readable draft** | The document SunBridge would actually hand to the agent (Markdown, PDF, or HTML). Generated by your pipeline, not written by hand.[cite: 5] |

### 2. Video walkthrough (3–8 minutes)[cite: 5]
Screen recording covering what you built, the pipeline running, and one thing that went wrong or that you'd change. Upload to Drive, Loom, or unlisted YouTube and submit the link with your repo.[cite: 5]

### 3. Submitting[cite: 5]
Submission is done through the official Cantordust application form — this document is the task brief only, not the submission channel. Use the form to send in your GitHub repo link and your video link.[cite: 5]

---

## A note on scope[cite: 5]

48 hours. We are not expecting a production system. Rough edges, TODOs, and honest "this doesn't handle X yet" notes in your README are fine, and often score better than a polished demo that hides its limits.[cite: 5]

What we don't want to see: a pipeline that only works because you already knew the answers.[cite: 5]
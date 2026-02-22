---
layout: default
title: Research
permalink: /research/
---

<h1>Research</h1>

<div class="search-box">
  <label for="research-filter">Filter by keyword (title, coauthor, year)</label>
  <input
    id="research-filter"
    type="search"
    placeholder="e.g. housing, 2025, Strumpf"
    data-index-url="{{ '/assets/search/papers_index.json' | relative_url }}"
  >
</div>

<section>
  <h2>Working Papers</h2>
  <ol class="research-list">
    {% for item in site.data.working_papers %}
    {% assign primary_link = item.external_url %}
    {% if primary_link == nil or primary_link == '' %}
      {% assign primary_link = item.pdf_path | relative_url %}
    {% endif %}
    {% assign abstract_text = item.abstract %}
    {% if abstract_text == nil or abstract_text == '' %}
      {% assign abstract_text = 'Abstract unavailable.' %}
    {% endif %}
    <li
      class="research-item"
      data-paper-id="{{ item.id | escape }}"
      data-search="{{ item.title | escape }} {{ item.authors | join: ' ' | escape }} {{ item.year }} {{ item.date | escape }}"
    >
      <p>
        {% if primary_link and primary_link != '' %}
        <a href="{{ primary_link }}" target="_blank" rel="noopener">{{ item.title }}</a>
        {% else %}
        {{ item.title }}
        {% endif %}
        {% if item.date and item.date != '' %} ({{ item.date }}){% elsif item.year and item.year != '' %} ({{ item.year }}){% endif %}
      </p>

      {% if item.coauthors and item.coauthors.size > 0 %}
      <p class="meta">with
        {% for coauthor in item.coauthors %}
          {% if coauthor.url %}<a href="{{ coauthor.url }}" target="_blank" rel="noopener">{{ coauthor.name }}</a>{% else %}{{ coauthor.name }}{% endif %}{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      </p>
      {% else %}
      <p class="meta">{{ item.authors | join: ', ' }}</p>
      {% endif %}

      <p class="inline-links">
        {% for l in item.links %}
          {% if l.url %}
          <a href="{{ l.url }}" target="_blank" rel="noopener">{{ l.label }}</a>
          {% else %}
          <span class="badge">{{ l.label }}</span>
          {% endif %}
        {% endfor %}
        {% if item.slides and item.slides.url %}
        <a href="{{ item.slides.url }}" target="_blank" rel="noopener">{{ item.slides.label | default: 'Slides' }}</a>
        {% endif %}
        {% for m in item.mentions %}
          {% if m.url %}
          <a class="badge" href="{{ m.url }}" target="_blank" rel="noopener">{{ m.label }}</a>
          {% endif %}
        {% endfor %}
        <button
          class="abstract-button js-view-abstract"
          type="button"
          data-paper-id="{{ item.id | escape }}"
          data-title="{{ item.title | escape }}"
          data-abstract="{{ abstract_text | escape }}"
          data-url="{{ primary_link | escape }}"
        >
          View Abstract
        </button>
      </p>
    </li>
    {% endfor %}
  </ol>
</section>

<section>
  <h2>Work in Progress</h2>
  <ul class="research-list">
    {% for item in site.data.research.work_in_progress %}
    <li class="research-item" data-search="{{ item | escape }}">{{ item }}</li>
    {% endfor %}
  </ul>
</section>

<section>
  <h2>Publications</h2>
  <ol class="research-list">
    {% for item in site.data.publications %}
    {% assign primary_link = item.external_url %}
    {% if primary_link == nil or primary_link == '' %}
      {% assign primary_link = item.pdf_path | relative_url %}
    {% endif %}
    {% assign abstract_text = item.abstract %}
    {% if abstract_text == nil or abstract_text == '' %}
      {% assign abstract_text = 'Abstract unavailable.' %}
    {% endif %}
    <li
      class="research-item"
      data-paper-id="{{ item.id | escape }}"
      data-search="{{ item.title | escape }} {{ item.authors | join: ' ' | escape }} {{ item.year }} {{ item.date | escape }}"
    >
      {% if item.citation and item.citation != '' %}
      <p>{{ item.citation }}</p>
      {% else %}
      <p>
        {% if primary_link and primary_link != '' %}
        <a href="{{ primary_link }}" target="_blank" rel="noopener">{{ item.title }}</a>
        {% else %}
        {{ item.title }}
        {% endif %}
        {% if item.date and item.date != '' %} ({{ item.date }}){% elsif item.year and item.year != '' %} ({{ item.year }}){% endif %}
      </p>
      {% endif %}

      {% if item.links and item.links.size > 0 %}
      <p class="inline-links">
        {% for l in item.links %}
          {% if l.url %}
          <a href="{{ l.url }}" target="_blank" rel="noopener">{{ l.label }}</a>
          {% else %}
          <span class="badge">{{ l.label }}</span>
          {% endif %}
        {% endfor %}
        <button
          class="abstract-button js-view-abstract"
          type="button"
          data-paper-id="{{ item.id | escape }}"
          data-title="{{ item.title | escape }}"
          data-abstract="{{ abstract_text | escape }}"
          data-url="{{ primary_link | escape }}"
        >
          View Abstract
        </button>
      </p>
      {% else %}
      <p class="inline-links">
        {% if primary_link and primary_link != '' %}
        <a href="{{ primary_link }}" target="_blank" rel="noopener">Paper Link</a>
        {% endif %}
        <button
          class="abstract-button js-view-abstract"
          type="button"
          data-paper-id="{{ item.id | escape }}"
          data-title="{{ item.title | escape }}"
          data-abstract="{{ abstract_text | escape }}"
          data-url="{{ primary_link | escape }}"
        >
          View Abstract
        </button>
      </p>
      {% endif %}
    </li>
    {% endfor %}
  </ol>
</section>

<section>
  <h2>Other Working Papers</h2>
  <ul class="research-list">
    {% for item in site.data.research.other_working_papers %}
    <li class="research-item" data-search="{{ item.title | escape }}">
      <p>{% if item.url %}<a href="{{ item.url }}" target="_blank" rel="noopener">{{ item.title }}</a>{% else %}{{ item.title }}{% endif %}</p>
      {% if item.coauthors %}
      <p class="meta">with
        {% for coauthor in item.coauthors %}
          {% if coauthor.url %}<a href="{{ coauthor.url }}" target="_blank" rel="noopener">{{ coauthor.name }}</a>{% else %}{{ coauthor.name }}{% endif %}{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      </p>
      {% endif %}
      {% if item.mentions %}
      <p class="inline-links">
        {% for m in item.mentions %}
        <a class="badge" href="{{ m.url }}" target="_blank" rel="noopener">{{ m.label }}</a>
        {% endfor %}
      </p>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
</section>

<script src="{{ '/assets/js/research-filter.js' | relative_url }}" defer></script>

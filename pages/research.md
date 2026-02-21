---
layout: default
title: Research
permalink: /research/
---

<h1>Research</h1>

<div class="search-box">
  <label for="research-filter">Filter by keyword (title, coauthor, year)</label>
  <input id="research-filter" type="search" placeholder="e.g. housing, 2025, Strumpf">
</div>

<section>
  <h2>Working Papers</h2>
  <ol class="research-list">
    {% for item in site.data.research.working_papers %}
    <li class="research-item" data-search="{{ item.title | escape }} {{ item.month | escape }} {{ item.year }} {% for c in item.coauthors %}{{ c.name | escape }} {% endfor %}">
      <p><a href="{{ item.url }}" target="_blank" rel="noopener">{{ item.title }}</a>{% if item.subtitle %} {{ item.subtitle }}{% endif %} ({{ item.month }} {{ item.year }})</p>
      {% if item.coauthors %}
      <p class="meta">with
        {% for coauthor in item.coauthors %}
          {% if coauthor.url %}<a href="{{ coauthor.url }}" target="_blank" rel="noopener">{{ coauthor.name }}</a>{% else %}{{ coauthor.name }}{% endif %}{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      </p>
      {% endif %}
      <p class="inline-links">
        {% for l in item.links %}
          {% if l.url %}
          <a href="{{ l.url }}" target="_blank" rel="noopener">{{ l.label }}</a>
          {% else %}
          <span class="badge">{{ l.label }}</span>
          {% endif %}
        {% endfor %}
        {% if item.slides %}<a href="{{ item.slides.url }}" target="_blank" rel="noopener">{{ item.slides.label }}</a>{% endif %}
        {% for m in item.mentions %}
          <a class="badge" href="{{ m.url }}" target="_blank" rel="noopener">{{ m.label }}</a>
        {% endfor %}
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
    {% for item in site.data.research.publications %}
    <li class="research-item" data-search="{{ item.citation | escape }}">
      <p>{{ item.citation }}</p>
      {% if item.links %}
      <p class="inline-links">
        {% for l in item.links %}
        <a href="{{ l.url }}" target="_blank" rel="noopener">{{ l.label }}</a>
        {% endfor %}
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

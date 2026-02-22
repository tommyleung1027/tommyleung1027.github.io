---
layout: default
title: Home
---

<section class="hero">
  <div class="hero-layout">
    <div>
      <h1>{{ site.data.site.name }}</h1>
      <p class="lead">{{ site.data.site.role }}, {{ site.data.site.department }}</p>
      {% for position in site.data.site.past_positions %}
      <p>{{ position }}</p>
      {% endfor %}
      <p>I am the co-organizer of the <a href="{{ site.data.site.links.vide.url }}" target="_blank" rel="noopener">VIDE seminar series</a>.</p>
    </div>
    <div>
      <img class="profile-photo" src="{{ '/picture/profile.jpg' | relative_url }}" alt="Tin Cheuk Leung portrait">
    </div>
  </div>
</section>

<section>
  <h2>Research Interests</h2>
  <ul>
    {% for interest in site.data.site.research_interests %}
    <li>{{ interest }}</li>
    {% endfor %}
  </ul>
</section>

<section class="two-col">
  <div>
    <h2>Contact</h2>
    <p><strong>Email:</strong> <a href="mailto:{{ site.data.site.contact.email }}">{{ site.data.site.contact.email }}</a></p>
    <p><strong>Office phone:</strong> {{ site.data.site.contact.phone }}</p>
    <p><strong>Office:</strong> {{ site.data.site.contact.office }}</p>
    <p><strong>Mailing address:</strong> {{ site.data.site.contact.address }}</p>
  </div>
  <div>
    <h2>Links</h2>
    <ul class="icon-links">
      <li><a href="{{ site.data.site.links.scholar.url }}" target="_blank" rel="noopener" aria-label="Google Scholar profile">[Scholar] {{ site.data.site.links.scholar.label }}</a></li>
      <li><a href="{{ site.data.site.links.twitter.url }}" target="_blank" rel="noopener" aria-label="X profile">[X] {{ site.data.site.links.twitter.label }}</a></li>
      <li><a href="{{ site.data.site.links.linkedin.url }}" target="_blank" rel="noopener" aria-label="LinkedIn profile">[in] {{ site.data.site.links.linkedin.label }}</a></li>
      <li><a href="{{ site.data.site.links.vide.url }}" target="_blank" rel="noopener" aria-label="VIDE seminar series">[VIDE] {{ site.data.site.links.vide.label }}</a></li>
    </ul>
  </div>
</section>

<section>
  <h2>Featured Working Papers</h2>
  <div class="paper-list">
    {% assign featured = site.data.working_papers | where: 'featured', true %}
    {% for item in featured limit:4 %}
    {% assign primary_link = item.external_url %}
    {% if primary_link == nil or primary_link == '' %}
      {% assign primary_link = item.pdf_path | relative_url %}
    {% endif %}
    {% assign abstract_text = item.abstract %}
    {% if abstract_text == nil or abstract_text == '' %}
      {% assign abstract_text = 'Abstract unavailable.' %}
    {% endif %}
    <article class="paper-card compact">
      <h3 class="paper-title">
        {% if primary_link and primary_link != '' %}
        <a href="{{ primary_link }}" target="_blank" rel="noopener">{{ item.title }}</a>
        {% else %}
        {{ item.title }}
        {% endif %}
      </h3>
      {% if item.date and item.date != '' %}
      <p class="meta compact-line">{{ item.date }}</p>
      {% elsif item.year and item.year != '' %}
      <p class="meta compact-line">{{ item.year }}</p>
      {% endif %}
      <p class="inline-links compact-line">
        {% if item.external_url and item.external_url != '' %}
        <a href="{{ item.external_url }}" target="_blank" rel="noopener">Paper Link</a>
        {% endif %}
      </p>
      <p class="meta compact-line">{{ item.authors | join: ', ' }}</p>
      <p class="compact-line">
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
    </article>
    {% endfor %}
  </div>
</section>

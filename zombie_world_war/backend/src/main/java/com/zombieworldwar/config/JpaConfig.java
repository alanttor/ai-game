package com.zombieworldwar.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableJpaRepositories(basePackages = "com.zombieworldwar.repository")
@EnableJpaAuditing
@EnableTransactionManagement
public class JpaConfig {
    // JPA configuration is handled via application.yml
    // This class enables JPA repositories and auditing
}

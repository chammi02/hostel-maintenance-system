package com.hostel.maintenance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@SpringBootApplication
public class HostelApplication {

    public static void main(String[] args) {
        SpringApplication.run(HostelApplication.class, args);
        System.out.println("=====================================================");
        System.out.println(" Hostel Maintenance Spring Boot Backend Started! ");
        System.out.println(" API Port: http://localhost:8080 ");
        System.out.println("=====================================================");
    }

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOrigins("*")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS");
            }
        };
    }
}

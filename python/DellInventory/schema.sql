--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.11
-- Dumped by pg_dump version 9.6.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: disks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.disks (
    hostname character varying(60),
    busType character varying(6),
    partNumber character varying(25),
    slot character varying(10),
    formFactor character varying(12),
    mediaType character varying(6),
    capacity integer
);


ALTER TABLE public.disks OWNER TO postgres;

--
-- Name: interfaces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interfaces (
    macAddress character varying(20) NOT NULL,
    hostname character varying(60),
    ifaceName character varying(20),
    ipAddress character varying(15),
    driver character varying(15),
    inUse boolean
);


ALTER TABLE public.interfaces OWNER TO postgres;

--
-- Name: memory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.memory (
    hostname character varying(60),
    slot character varying(10),
    speed character varying(12),
    partNumber character varying(25),
    capacity integer
);


ALTER TABLE public.memory OWNER TO postgres;

--
-- Name: servers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.servers (
    serviceTag character varying(20),
    cpuModel text,
    cpuThreads smallint,
    memoryTotal integer,
    memoryType character varying(5),
    osFamily character varying(10),
    osVersion character varying(10),
    kernel character varying(60),
    hostname character varying(60),
    serverModel character varying(20),
    lastUpdate timestamp without time zone
);


ALTER TABLE public.servers OWNER TO postgres;

--
-- Name: disks disks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disks
    ADD CONSTRAINT disks_pkey PRIMARY KEY (hostname, slot);


--
-- Name: interfaces interfaces_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interfaces
    ADD CONSTRAINT interfaces_pkey PRIMARY KEY (hostname,ifaceName);

--
-- Name: memory memory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT memory_pkey PRIMARY KEY (hostname, slot);


--
-- Name: servers servers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servers
    ADD CONSTRAINT servers_pkey PRIMARY KEY (hostname);


--
-- Name: disks disks_host_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disks
    ADD CONSTRAINT disks_host_name_fkey FOREIGN KEY (hostname) REFERENCES public.servers(hostname) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: interfaces interfaces_host_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interfaces
    ADD CONSTRAINT interfaces_host_name_fkey FOREIGN KEY (hostname) REFERENCES public.servers(hostname) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: memory memory_host_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT memory_host_name_fkey FOREIGN KEY (hostname) REFERENCES public.servers(hostname) ON UPDATE CASCADE ON DELETE CASCADE;

--
-- PostgreSQL database dump complete
--


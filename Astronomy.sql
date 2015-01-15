--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: stars; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE stars (
    id bigint,
    name character varying NOT NULL,
    right_ascension double precision DEFAULT 0.0 NOT NULL,
    declination double precision DEFAULT 0.0 NOT NULL
);


ALTER TABLE public.stars OWNER TO postgres;

--
-- Name: Stars_ID_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "Stars_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Stars_ID_seq" OWNER TO postgres;

--
-- Name: Stars_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "Stars_ID_seq" OWNED BY stars.id;


--
-- Name: abundances; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE abundances (
    id integer NOT NULL,
    carbon double precision,
    oxygen double precision
);


ALTER TABLE public.abundances OWNER TO postgres;

--
-- Name: names; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE names (
    id integer,
    alternatenames character varying(50)
);


ALTER TABLE public.names OWNER TO postgres;

--
-- Name: temperatures; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE temperatures (
    id integer NOT NULL,
    temperature smallint
);


ALTER TABLE public.temperatures OWNER TO postgres;

--
-- Name: vr; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE vr (
    id integer,
    vr double precision,
    observationdate double precision
);


ALTER TABLE public.vr OWNER TO postgres;

--
-- Name: TABLE vr; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE vr IS 'Radial velocity';


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY stars ALTER COLUMN id SET DEFAULT nextval('"Stars_ID_seq"'::regclass);


--
-- Name: Stars_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY stars
    ADD CONSTRAINT "Stars_pkey" PRIMARY KEY (name);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--


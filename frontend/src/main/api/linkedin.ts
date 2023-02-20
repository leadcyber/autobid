import cheerio from 'cheerio'
import axios from 'axios'
import { FetchedJob, PageData } from '../../job.types';
import { myConsole } from '../util/myconsole';
import url from "url"
import path from "path"
import { workspaceSetting } from '../config/constant'
import { SocksProxyAgent } from "socks-proxy-agent"
import fs from 'fs'

const proxyPath = path.join(workspaceSetting.workspacePath, workspaceSetting.proxy)
const proxySetting = JSON.parse(fs.readFileSync(proxyPath).toString())

const httpsAgent = new SocksProxyAgent(proxySetting)
const myAxios = axios.create({httpsAgent})

export const query = (queryObject: any, onJobsFound: Function): Promise<void> => {
  const query = new Query(queryObject);
  return query.getJobs(onJobsFound);
};
export const getPageData = async (jobUrl: string): Promise<PageData> => {
  const { data } = await myAxios.get(jobUrl);

  //select data so we can check the number of jobs returned
  const $ = cheerio.load(data);
  const brief = $(".top-card-layout")
  const detail = $(".decorated-job-posting__details")
  const pageData = { brief: brief.html()!, detail: detail.html()! }

  const messageRecruiter = detail.find(".message-the-recruiter > div")
  const recruiter = messageRecruiter.length > 0 ? {
    image: messageRecruiter.find("img").data("delayedUrl"),
    name: messageRecruiter.find("h3").text()!,
    title: messageRecruiter.find("h4").text()!
  } : null


  const jdSection = detail.find(".description__text section div.show-more-less-html__markup")
  const jobDescription = jdSection.length > 0 ? jdSection.html() : ""

  const criteriaList = detail.find(".description__job-criteria-list li")
  const criterias: any = {}
  for(let i = 0; i < criteriaList.length; i ++) {
    const item = criteriaList.get(i)!
    const key = $(item).find(".description__job-criteria-subheader").text().trim()
    const value = $(item).find(".description__job-criteria-text").text().trim()
    criterias[key] = value
  }

  let applyData = {applyMode: "", applyUrl: ""}
  let applyButton = brief.find(".apply-button");
  if(applyButton.length == 0) {
    applyButton = brief.find("[data-tracking-control-name='public_jobs_apply-link-offsite_sign-up-modal']")
  }
  if(applyButton.length == 0) {
    applyData = {
      applyMode: "Closed",
      applyUrl: ""
    }
  } else {
    //if result count ends up being 0 we will stop getting more jobs
    let applyButtonText = applyButton.text()

    let externalUrl: string = ""

    if(applyButtonText.includes("Apply on company website")) {
      applyButtonText = "Apply"
      externalUrl = applyButton.attr("href") || ""
    }
    else if(applyButtonText.includes("Apply")) {
      const codeUrlElement = brief.find("#applyUrl")
      if(codeUrlElement.length > 0) {
        applyButtonText = "Apply"
        const urlMatch = codeUrlElement.html()!.match(/\"(.*?)\"/ig)!
        if(urlMatch == null) {
          applyButtonText = "EasyApply"
        } else {
          externalUrl = urlMatch[0].slice(1, -1)
        }
      } else {
        applyButtonText = "EasyApply"
      }
    }
    else applyButtonText = "Closed"


    let applyUrl: string = ""
    if(externalUrl != "") {
      const searchParam = new URLSearchParams(url.parse(externalUrl).query!)
      applyUrl = searchParam.get("url") || ""
    }
    console.log("applyUrl", applyUrl)

    applyData = {
      applyMode: applyButtonText as any,
      applyUrl: applyButtonText == "EasyApply" ? jobUrl : applyUrl
    }
  }
  return {
    ...pageData,
    ...applyData,
    recruiter,
    description: jobDescription,
    criterias
  } as PageData
}

class Query {
  host;
  keyword;
  location;
  dateSincePosted;
  jobType;
  remoteFilter;
  salary;
  experienceLevel;
  sortBy;
  limit;
  //transfers object values passed to our .query to an obj we can access
  constructor(queryObj: any) {
    //query vars
    this.host = queryObj.host || "www.linkedin.com";

    //api handles strings with spaces by replacing the values with %20
    this.keyword = queryObj.keyword || "";
    this.location = queryObj.location || "";
    this.dateSincePosted = queryObj.dateSincePosted || "";
    this.jobType = queryObj.jobType || "";
    this.remoteFilter = queryObj.remoteFilter || "";
    this.salary = queryObj.salary || "";
    this.experienceLevel = queryObj.experienceLevel || "";
    this.sortBy = queryObj.sortBy || "";
    //internal variable
    this.limit = Number(queryObj.limit) || 0;
  }

  /*
   * Following get Functions act as object literals so the query can be constructed with the correct parameters
   */
  getDateSincePosted = () => {
    const dateRange: any = {
      "past month": "r2592000",
      "past week": "r604800",
      "24hr": "r86400",
    };
    return dateRange[this.dateSincePosted.toLowerCase()] ?? "";
  };

  getExperienceLevel = () => {
    const experienceRange: any = {
      internship: "1",
      "entry level": "2",
      associate: "3",
      senior: "4",
      director: "5",
      executive: "6",
    };
    return experienceRange[this.experienceLevel.toLowerCase()] ?? "";
  };
  getJobType = () => {
    return this.jobType
    // const jobTypeRange: any = {
    //   "full time": "F",
    //   "full-time": "F",
    //   "part time": "P",
    //   "part-time": "P",
    //   contract: "C",
    //   temporary: "T",
    //   volunteer: "V",
    //   internship: "I",
    // };
    // return jobTypeRange[this.jobType.toLowerCase()] ?? "";
  };
  getRemoteFilter = () => {
    const remoteFilterRange: any = {
      "on-site": "1",
      "on site": "1",
      remote: "2",
      hybrid: "3",
    };
    return remoteFilterRange[this.remoteFilter.toLowerCase()] ?? "";
  };
  getSalary = () => {
    const salaryRange: any = {
      40000: "1",
      60000: "2",
      80000: "3",
      100000: "4",
      120000: "5",
    };
    return salaryRange[this.salary.toLowerCase()] ?? "";
  };

  /*
   * EXAMPLE OF A SAMPLE QUERY
   * https://www.linkedin.com/jobs/search/?f_E=2%2C3&f_JT=F%2CP&f_SB2=1&f_TPR=r2592000&f_WT=2%2C1&geoId=90000049&keywords=programmer&location=Los%20Angeles%20Metropolitan%20Area
   * Date Posted (Single Pick)	        f_TPR
   * Job Type (Multiple Picks)	        f_JT
   * Experience Level(Multiple Picks)	    f_E
   * On-Site/Remote (Multiple Picks)	    f_WT
   * Salary (Single Pick)	                f_SB2
   *
   */
  url = (start: number) => {
    let query = `https://${this.host}/jobs-guest/jobs/api/seeMoreJobPostings/search?`;
    if (this.keyword !== "") query += `keywords=${this.keyword}`;
    if (this.location !== "") query += `&location=${this.location}`;
    if (this.getDateSincePosted() !== "")
      query += `&f_TPR=${this.getDateSincePosted()}`;
    if (this.getSalary() !== "") query += `&f_SB2=${this.getSalary()}`;
    if (this.getExperienceLevel() !== "")
      query += `&f_E=${this.getExperienceLevel()}`;
    if (this.getRemoteFilter() !== "")
      query += `&f_WT=${this.getRemoteFilter()}`;
    if (this.getJobType() !== "") query += `&f_JT=${this.getJobType()}`;
    query += `&start=${start}`;
    if (this.sortBy == "recent" || this.sortBy == "relevant") {
      let sortMethod = "R";
      if (this.sortBy == "recent") sortMethod = "DD";
      query += `&sortBy=${sortMethod}`;
    }
    return encodeURI(query);
  };

  getJobs = async (onJobsFound: Function): Promise<void> => {
//    let allJobs: FetchedJob[] = [];
    let allJobsCount = 0
    try {
      let parsedJobs,
        resultCount = 1,
        start = 0,
        jobLimit = this.limit;


      while (resultCount > 0) {
        //fetch our data using our url generator with
        //the page to start on
        let data: any = null
        try {
          // console.log(`[fetching]: ${this.url(start)}`)
          myConsole.log(`[fetching]: ${this.url(start)}`)
          data = (await myAxios.get(this.url(start))).data;
        } catch(err) {
          continue
        }

        //select data so we can check the number of jobs returned
        const $ = cheerio.load(data);
        const jobs = $("li");
        //if result count ends up being 0 we will stop getting more jobs
        resultCount = jobs.length;
        console.log(resultCount)

        //to get the job data as objects with the desired details
        parsedJobs = parseJobList(data);
        // allJobs.push(...parsedJobs);
        await onJobsFound(parsedJobs, start)
        allJobsCount += parsedJobs.length

        //increment by 25 bc thats how many jobs the AJAX request fetches at a time
        start += 25;

        //in order to limit how many jobs are returned
        //this if statment will return our function value after looping and removing excess jobs
        // if (jobLimit != 0 && allJobs.length > jobLimit) {
        //   while (allJobs.length != jobLimit) allJobs.pop();
        //   return allJobs;
        // }
        if(jobLimit != 0 && allJobsCount >= jobLimit) return
      }
      // return allJobs;
    } catch (error: any) {
      myConsole.error(`Error code: ${error.code}`);
      console.error(`Error code: ${error.code}`);
      // return allJobs
    }
  };
}

function parseJobList(jobData: any): FetchedJob[] {
  const $ = cheerio.load(jobData);
  const jobs = $("li");

  const jobObjects = jobs
    .map((index: number, element: any) => {
      const job = $(element);
      const position = job.find(".base-search-card__title").text().trim() || "";
      const company =
        job.find(".base-search-card__subtitle").text().trim() || "";
      const location =
        job.find(".job-search-card__location").text().trim() || "";
      const postedDate = job.find("time").attr("datetime") || "";
      const postedAgo = job.find("time").text().trim() || "";
      const salary =
        job
          .find(".job-search-card__salary-info")
          .text()
          .trim()
          .replace(/\n/g, "")
          .replaceAll(" ", "") || "";
      let jobUrl = job.find(".base-card__full-link").attr("href") || "";
      jobUrl = `https://www.linkedin.com${url.parse(jobUrl).pathname}`
      return {
        position: position,
        company: company,
        location: location,
        postedAgo: postedAgo,
        postedDate: postedDate,
        salary: salary,
        jobUrl: jobUrl,
      };
    })
    .get();

  return jobObjects;
}
